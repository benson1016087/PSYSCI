from psychopy import visual, core, event, monitors, tools, gui
import numpy as np
import random, time


all_colors = [[1, 0, 0], # 0 -> Red
			  [0, 0, 1], # 1 -> Blue
			  [0.93, 0.009, 0.93], # 2 -> Violet
			  [0, 1, 0], # 3 -> Green
			  [1, 1, 0], # 4 -> Yellow
			  [-1, -1, -1], # 5 -> Black
			  [1, 1, 1], # 6 -> White
			  [0, 0, 0]  # 7 -> Gray
			 ]

subj_id = -1
condition = -1

## Initial the response variable.
response_key = []
response_time = []
response_correctornot = [] 

def save_behavioral_data(subject_id, trials, trials_key, trials_rt, trial_correct):
	trial_info = trials
	output = {
		'response_key': trials_key,
		'response_time': trials_rt,
		'correct': trial_correct
	}
	response_info = pd.DataFrame(output) 

def starting_information():
	# Clocks
	clock_trial = core.Clock() 
	win = visual.Window(size=[800, 600], units="norm",fullscr=False, color=[0, 0, 0])

	# Prepare the instruction
	text = visual.TextStim(win=win, pos=[0, 0], color=[-1,-1,-1])
	
	# Display the instruction
	text.text = '''
	 Your task is to as accurately and quickly as possible to Your task is to as accurately and quickly as possible to identify whether the squares'colors between encode and probe period isidentical.
	'''
	text.draw()
	win.flip()
	event.waitKeys(5)
	win.close()

def trail_func(color_set, wait_time, chosen_dim, with_cross = True):
	# Parameters of object
	num_check = 5 # total number
	block_size = tools.monitorunittools.deg2pix(0.65, monitor=mon) # size of the block
	location = [0, 0]		
	interval = tools.monitorunittools.deg2pix(2, monitor=mon) # size of the interval
	check_size = [block_size, block_size] 	
	color_of_quadrant = color_set

	# Set blocks information
	loc = np.array(location) + np.array(check_size) // 2
	low, high = num_check // -2, num_check // 2
	xys = []
	if abs(low) != high:
		low += 1
		high += 1
	for y in range(low, high):
		i = 0
		for x in range(low, high):
			# let even block place a little lower
			if i % 2 == 1:
				y_delta = -check_size[0] / 2
			else:
				y_delta = 0
			i += 1

			xys.append(((check_size[0] + interval) * x, (check_size[1] + interval) * y + y_delta))

	# Set colors
	colors = [[0, 0, 0]] * (num_check ** 2)
	quadrant_base_idx = [18, 15, 0, 3]
	for i in range(4):
		colors[quadrant_base_idx[i] + chosen_dim[i]] = all_colors[color_set[i]]

	if with_cross == True:
		text_cross = visual.TextStim(win=win, pos=[0, 0], color=[-1, -1, -1], text="+", units="norm")
		text_cross.draw()
		
	# Draw blocks
	stim = visual.ElementArrayStim(win, units="pix", xys=xys, fieldPos=loc, colors=colors,
								   nElements=num_check**2, elementMask=None,
								   elementTex=None, sizes= block_size)

	stim.draw()
	win.flip()
	if wait_time < 0:
		expect = ['c', 'm', 'C', 'M']
		c = event.waitKeys(maxWait=2, keyList=expect)
		if c == None:
			return 'n'
		return c[0].lower()
	else:
		core.wait(wait_time)
	
def one_trail(encode, probe):
	dim_rd_place = np.random.choice([0, 1, 5, 6], 4)
	trail_func([7, 7, 7, 7], 0.2, dim_rd_place, True)
	trail_func(encode, 0.1, dim_rd_place)
	trail_func([7, 7, 7, 7], 0.9, dim_rd_place, True)
	initial_time = time.clock()
	result = trail_func(probe, -1, dim_rd_place)
	response_time = time.clock()
	trail_func([7, 7, 7, 7], 0.7, dim_rd_place)

	return result, response_time - initial_time

def one_session(seq, f):
	for i in seq:
		if i[-1] == '\n':
			i = i[:-1]
		inp = [int(j) - 1 for j in i.split(',')]
		r, t = one_trail(inp[:4], inp[4:8])
		res_ans = -1
		if r == 'm':
			res_ans = 1
		elif r == 'c':
			res_ans = 0
		
		f.write(i + ',{},{},{}\n'.format(r, t, int(res_ans == inp[-1] + 1)))

if __name__ == '__main__': # The code start from here
	# Subject's information
	gui = gui.Dlg()
	gui.addField("Subject ID:")
	gui.addField("condition")
	gui.show()

	subj_id = gui.data[0]
	condition = gui.data[1]

	# Initialize the environment
	starting_information()
	mon = monitors.Monitor(name='mypc', width=37, distance=60)
	mon.setSizePix((800, 600))
	win = visual.Window(size=[800,600], units='pix')
	if int(condition) == 1:
		trial_file_session1 = 'set2.csv'
		trial_file_session2 = 'set4.csv'
	elif int(condition) == 2:
		trial_file_session1 = 'set4.csv'
		trial_file_session2 = 'set2.csv'
	else:
		print("Condition number error!!")
		exit()

	# Read / write file
	with open(trial_file_session1, 'r') as f:
		s1 = f.readlines()
	with open(trial_file_session2, 'r') as f:
		s2 = f.readlines()

	f_w = open(subj_id + '.csv', 'w')
	f_w.write(s1[0][:-1] + ',response_key,response_time,correct\n')

	# Start the experiment
	text2 = visual.TextStim(win=win, color=[-1, -1, -1], pos=(0, 0),
							text='''Session 1\nPress any key to start\nM for the same\nC for the different\n'''
							)
	text2.draw()
	win.flip()
	core.wait(.6)

	one_session(s1[1:], f_w) 
	one_session(s2[1:], f_w) 

	# Finish
	text2.text = '''
	The experiment is done,
	Please notify the experimental leader
	Press space to end the experiment
	'''
	text2.draw()
	win.flip()
	event.waitKeys()
	win.close()
	core.quit()