


(define (problem tsp-4)
(:domain tsp)
(:objects p1 p2 p3 p4 - location )
(:init
(in p1)
(connected p1 p3)
(connected p3 p1)
(connected p1 p4)
(connected p4 p1)
(connected p3 p2)
(connected p2 p3)
)
(:goal
(and
(visited p1)
(visited p2)
(visited p3)
(visited p4)
)
)
)


