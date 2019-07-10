(define (domain tsp)
(:requirements :negative-preconditions :typing)
(:types location - object)
  (:predicates
  ( in ?x - location)
  ( visited ?x  - location)
  ( connected ?x ?y - location) 
)

  (:action move
	:parameters (?x ?y - location)
	:precondition (and (in ?x) (not (visited ?y)) (connected ?x ?y))
	:effect (and (in ?y) (visited ?y) (not (in ?x)))))
