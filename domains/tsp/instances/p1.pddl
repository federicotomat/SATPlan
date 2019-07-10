


(define (problem tsp-2)
(:domain tsp)
(:objects 
	p1 - location
	p2 - location
)
(:init
(in p1)
(connected p1 p2)
(connected p2 p1)
)
(:goal
(and (visited p1) (visited p2))))


