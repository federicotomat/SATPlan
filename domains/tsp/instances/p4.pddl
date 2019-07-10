

(define (problem tsp-5)
(:domain tsp)
(:objects p1 p2 p3 p4 p5 - location)
(:init
(in p1)
(connected p1 p2)
(connected p2 p1)
(connected p3 p2)
(connected p2 p3)
(connected p3 p4)
(connected p4 p3)
(connected p5 p3)
(connected p3 p5)
(connected p5 p4)
(connected p4 p5)
)
(:goal
(and
(visited p2)
(visited p3)
(visited p4)
(visited p5)
)
)
)

