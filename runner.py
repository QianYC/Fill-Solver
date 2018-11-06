from solver import Solve
from converter import Converter

if __name__=='__main__':
	converter=Converter()
	map=converter.to_matrix('test3.png')
	solve=Solve()
	solution=solve.solve(map)
	print('solution = ',solution)
	converter.visualize_solution(solution,'test3.png',True)
