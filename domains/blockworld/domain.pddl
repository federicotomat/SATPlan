(define (domain blocksworld)
(:requirements :strips :equality :typing)
(:types block - object)
(:predicates (clear ?x - block)
             (on-table ?x - block)
             (arm-empty)
             (holding ?x - block)
             (on ?x ?y - block))

(:action pickup
  :parameters (?x - block)
  :precondition (and (clear ?x) (on-table ?x) (arm-empty))
  :effect (and (holding ?x) (not (clear ?x)) (not (on-table ?x)) (not (arm-empty))))

(:action putdown
  :parameters  (?x - block)
  :precondition (and (holding ?x))
  :effect (and (clear ?x) (arm-empty) (on-table ?x) 
               (not (holding ?x))))

(:action stack
  :parameters  (?x ?y - block)
  :precondition (and  (clear ?y) (holding ?x))
  :effect (and (arm-empty) (clear ?x) (on ?x ?y)
               (not (clear ?y)) (not (holding ?x))))

(:action unstack
  :parameters  (?x ?y - block)
  :precondition (and (on ?x ?y) (clear ?x) (arm-empty))
  :effect (and (holding ?x) (clear ?y)
               (not (on ?x ?y)) (not (clear ?x)) (not (arm-empty)))))
                      
