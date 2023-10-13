# import datetime
# from gym import MarsMarsEnv
#
# start_time = datetime.datetime.now().timestamp()
# env = MarsMarsEnv(render_mode=None)
# for i in range(10000):
#     obs, rew, term, trunc, info = env.step(env.action_space.sample())
#     # print(rew, term)
#     if term:
#         env.reset()
# env.close()
# end_time = datetime.datetime.now().timestamp()
# print(f"FPS: {10000 / (end_time - start_time)}")

from entities import Scene

game = Scene(render=True, interactive=True, debug_raycasting=True)
game.run()
