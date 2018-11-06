import config

class Solve():
	def __init__(self):
		self.solution=[]

	def solve(self,map):
		start=()

		for i in range(len(map)):
			for j in range(len(map[0])):
				if map[i][j]==config.START:
					start=(i,j)
					break
			if start!=():
				break

		self.backtrace_recursive(map,[start])
		return self.solution

	def backtrace_recursive(self,map, steps):
		if self.is_full(map):
			# print('steps = ',steps)
			self.solution = steps.copy()
			return

		last_pos = steps[-1]
		x = last_pos[0]
		y = last_pos[1]
		if x - 1 >= 0 and map[x - 1][y] == config.EMPTY:
			map[x - 1][y] = config.VISITED
			steps.append((x - 1, y))
			self.backtrace_recursive(map, steps)
			map[x - 1][y] = config.EMPTY
			steps.pop()

		if x + 1 < len(map) and map[x + 1][y] == config.EMPTY:
			map[x + 1][y] = config.VISITED
			steps.append((x + 1, y))
			self.backtrace_recursive(map, steps)
			map[x + 1][y] = config.EMPTY
			steps.pop()

		if y - 1 >= 0 and map[x][y - 1] == config.EMPTY:
			map[x][y - 1] = config.VISITED
			steps.append((x, y - 1))
			self.backtrace_recursive(map, steps)
			map[x][y - 1] = config.EMPTY
			steps.pop()

		if y + 1 < len(map[0]) and map[x][y + 1] == config.EMPTY:
			map[x][y + 1] = config.VISITED
			steps.append((x, y + 1))
			self.backtrace_recursive(map, steps)
			map[x][y + 1] = config.EMPTY
			steps.pop()

	def is_full(self,map):
		for i in range(len(map)):
			for j in range(len(map[0])):
				if map[i][j] == config.EMPTY:
					return False
		return True




