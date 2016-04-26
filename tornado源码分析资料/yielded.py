#encoding=utf-8

def generator(param):
	print "start"
	m = yield param
	print m
	m += 12
	m = yield m
	m2 = yield m+1
	print m

yielded = generator(3)
a = yielded.next()
b = yielded.send() #这个0会传递给第5行的yield表达式，因此m=0，结果就是输出了0

print "a,b:",a,b