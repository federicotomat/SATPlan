


(define (problem tsp-6)
(:domain tsp)
(:objects p1 p2 p3 p4 p5 p6 - location)
(:init
(in p1)
(connected p1 p2)
(connected p2 p1)
(connected p1 p3)
(connected p3 p1)
(connected p1 p4)
(connected p4 p1)
(connected p1 p5)
(connected p5 p1)
(connected p3 p2)
(connected p2 p3)
(connected p3 p4)
(connected p4 p3)
(connected p3 p5)
(connected p5 p3)
(connected p3 p6)
(connected p6 p3)
(connected p5 p2)
(connected p2 p5)
)
(:goal
(and
(visited p1)
(visited p2)
(visited p3)
(visited p4)
(visited p5)
(visited p6)
)
)
)


