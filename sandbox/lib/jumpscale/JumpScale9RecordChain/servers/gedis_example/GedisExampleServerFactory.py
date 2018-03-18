from pprint import pprint
from concurrent.futures import ThreadPoolExecutor
from js9 import j
import time
from .GedisExampleServer import GedisExampleServer
now = lambda: time.time()

JSBASE = j.application.jsbase_get_class()
import signal

class GedisExampleServerFactory(JSBASE):

    def __init__(self):
        self.__jslocation__ = "j.servers.gedisexample"
        JSBASE.__init__(self)

    def get(self):
        return GedisExampleServer()

    def start(self,background=True):
        """
        js9 'j.servers.gedisexample.start()'
        """
        if background:
            cmd = "js9 'j.servers.gedisexample.start(background=False)'"
            j.tools.tmux.execute(cmd, session='main', window='gedisexample',pane='main', session_reset=False, window_reset=True)
            j.sal.nettools.waitConnectionTest("localhost",8889)
        else:
            s = GedisExampleServer(port=8889)
            s.start()

        

    def test(self, dobenchmarks=True):
        """
        js9 'j.servers.gedisexample.test()'

        will start in tmux the server & then connect to it using redisclient

        """
        j.servers.zdb.start(instance="test",port=8888,reset=True)
        self.start()

        redis_client = j.clients.redis_config.get_by_params(
            instance='gedisexample', ipaddr='localhost', port=8889, password='', unixsocket='', ardb_patch=False, set_patch=True)
        r = redis_client.redis

        # assert True == r.ping()
        assert r.execute_command("PING") == True #is it binary or can it also return string
        assert r.execute_command("TESTB") == b'testworked'
        assert r.execute_command("TESTA") == b'testworked'

        error=False
        try:
            r.execute_command("ERROR") #should raise error
        except Exception as e:
            error=True
        assert error
        self.logger.info("[+]Test passed")

        #PERFORMANCE TEST
        def perf_test():
            futures = []
            MAX_NUM = 20000
            start = now()
            self.logger.info("Started benching with {}".format(MAX_NUM))
            with ThreadPoolExecutor(max_workers=4) as executor:
                for i in range(MAX_NUM):
                    # future = executor.submit(r.execute_command, "TESTA")
                    future = executor.submit(r.execute_command, "SET", b"AKEY", b"AVALUE")                    
                    futures.append(future)
            
            self.logger.debug("FUTURES LEN: %s"% len(futures))

            ## ASSERT ALL DONE, if not all done will assert error
            assert all([f.done() for f in futures])

            delta = now() - start          
            donefutures_len = len(futures)
            self.logger.debug("DONE COMMANDS {} in {} seconds  =>  {} command/second".format( donefutures_len, delta, donefutures_len/int(delta)))
            assert  donefutures_len/int(delta)>2000
            return int(donefutures_len / delta)

        def bench(times=1):
            return sum([perf_test() for i in range(times)]) / times

        if dobenchmarks:
            #[+]Average: 6624.2 commands/second
            self.logger.info("[+]Average: {} commands/second".format(bench()))

    
    # def test2(self, dobenchmarks=True):
    #     """
    #     js9 'j.servers.gedisexample.test()'

    #     will start in tmux the server & then connect to it using redisclient

    #     """
    #     cmd = "js9 'j.servers.gedisexample.start()'"
    #     j.tools.tmux.execute(cmd, session='main', window='gedisexample',pane='main', session_reset=False, window_reset=True)

    #     redis_client = j.clients.redis_config.get_by_params(
    #         instance='gedisexample', ipaddr='localhost', port=9999, password='', unixsocket='', ardb_patch=False, set_patch=True)
    #     r = redis_client.redis
    #     # r = j.clients.redis.get(port=9999)

    #     self.logger.info("Started test2")
    #     # assert True == r.ping()
    #     assert r.execute_command("PING") == True #is it binary or can it also return string
    #     assert r.execute_command("TESTB") == b'testworked'
    #     assert r.execute_command("TESTA") == b'testworked'
    #     self.logger.info("First assersions passed")
    #     try:
    #         for i in range(100):
    #             k = r.execute_command("SET", "a{}".format(i), "dmdm")
    #             # self.logger.info("NEW KEY: {}".format(k))
    #             value = r.execute_command("GET", k)
    #             # print("VAL: ", value)
    #             assert value == b"dmdm"
    #     except Exception as e:
    #         print("ERROR: ", e)
    #     self.logger.info("Batch assertions done")
        
    #     self.logger.info("[+]Test passed")

    #     #PERFORMANCE TEST
    #     def perf_test():
    #         futures = []
    #         MAX_NUM = 200000
    #         start = now()
    #         self.logger.info("Started benching with {}".format(MAX_NUM))
    #         with ThreadPoolExecutor(max_workers=4) as executor:
    #             for i in range(MAX_NUM):
    #                 future = executor.submit(r.execute_command, "SET", b"AKEY", b"AVALUE")
    #                 futures.append(future)
            
    #         self.logger.debug("FUTURES LEN: ", len(futures))
    #         ## ASSERT ALL DONE
    #         while not all([f.done() for f in futures]):
    #             continue

    #         delta = now() - start          
    #         donefutures_len = len(futures)
    #         self.logger.debug("DONE COMMANDS {} in {} seconds  =>  {} command/second".format( donefutures_len, delta, donefutures_len/int(delta)))
    #         return int(donefutures_len / delta)

    #     def bench(times=5):
    #         return sum([perf_test() for i in range(times)]) / times

    #     if dobenchmarks:
    #         # * [+]Average: 3883.2 commands/second
    #         self.logger.info("[+]Average: {} commands/second".format(bench())) 