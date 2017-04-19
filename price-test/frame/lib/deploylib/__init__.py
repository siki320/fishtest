"""
.
        ##   ##  #####             ###
         ##  ##  ##   ##           ##             ####      
         ### ##   ##  ##        #########            #
         ## ###  #####    ##     ##               ## 
        ##   ##  ##       ##      ##                 #
       ##   ##  ##      ####     ##              ###
       ##   ##  ##     ## ###      #####         
     ------------------## --##--------------------------------------
Original intention: Nova Perfermance auto test (Npat) v 3.0.0

A Environment building library for python.

Usage:
    class as(BaseModule):
        def localize1():
            pass
        def localize2():
            pass

    class frame(Env):
        asdemo = as()
        asdemo.register_module(asdemo,Npatlog)

frame.single_thread_run(localize1)
"""
