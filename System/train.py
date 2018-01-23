from System import System

system = System()
system.setup()

for episode in range(system.args.max_episodes):
	system.episode_step()
	for step in range(system.args.max_steps):
		system.complete_step()
