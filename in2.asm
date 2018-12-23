				go  0
	0			ld  1 .count
				ld 2 .vals1
				ld 3 .vals2
				ldi 5 0
	.loop			add 5 2
				add 5 3
				st  5 .result
				inc 3
				inc 2
				dec 1
				bnz 1 .loop
				sys 1 16
	.count			dw  3
	.vals1			dw  1
	.vals2  		dw  4
	.result 		dw  0
	16			dw  0
				end
