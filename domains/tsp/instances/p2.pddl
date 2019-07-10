(define (problem tsp-3)
(:domain tsp)
(:objects p1 p2 p3 - location )
(:init
(in p2)
(connected p1 p2)
(connected p2 p1)
(connected p3 p2)
(connected p2 p3)
)
(:goal
(and
(visited p1)
(visited p2)
(visited p3)
)
)
)


