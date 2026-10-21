"""Sample process-tree CPU/RAM and disk without blocking the renderer."""
import json
from pathlib import Path
import shutil
import threading
import time
import psutil

class Monitor:
    def __init__(self,out):
        self.out=Path(out);self.stop_event=threading.Event();self.root=psutil.Process()
        initial=self.root.cpu_times();self.initial_cpu=initial.user+initial.system
        self.cpu={};self.peak_rss=0;self.peak_cpu=0;self.minimum_free=shutil.disk_usage(out).free;self.samples=0
        self.previous=None;self.started=time.monotonic()
        self.thread=threading.Thread(target=self.loop,daemon=True);self.thread.start()

    def loop(self):
        while not self.stop_event.is_set():
            rss=0
            try:processes=[self.root,*self.root.children(recursive=True)]
            except psutil.Error:processes=[self.root]
            for p in processes:
                try:
                    stats=p.cpu_times();self.cpu[p.pid]=max(self.cpu.get(p.pid,0),stats.user+stats.system-(self.initial_cpu if p.pid==self.root.pid else 0))
                    rss+=p.memory_info().rss
                except psutil.Error:pass
            now=time.monotonic();total=sum(self.cpu.values())
            if self.previous:
                oldtime,oldtotal=self.previous
                self.peak_cpu=max(self.peak_cpu,100*max(0,total-oldtotal)/max(.001,now-oldtime))
            self.previous=(now,total);self.peak_rss=max(self.peak_rss,rss)
            self.minimum_free=min(self.minimum_free,shutil.disk_usage(self.out).free);self.samples+=1
            self.stop_event.wait(1)

    def stop(self):
        self.stop_event.set();self.thread.join(timeout=2)
        result={'wall_seconds':time.monotonic()-self.started,'samples':self.samples,
          'sampled_peak_process_tree_rss_mib':self.peak_rss/1024**2,
          'observed_process_tree_cpu_seconds':sum(self.cpu.values()),
          'peak_sampled_cpu_percent':self.peak_cpu,'minimum_disk_free_gib':self.minimum_free/1024**3,
          'limitations':'One-second samples can miss short-lived children; summed RSS may double-count shared pages. CPU percent is 100 per core. Local writing occurs before this render monitor; process lifetime peak RAM is also reported separately.'}
        (self.out/'resource-samples.json').write_text(json.dumps(result,indent=2))
        return result
