(define (domain gripper-strips)
(:requirements :strips :typing)
(:types room ball gripper - object)
   (:predicates (room ?r - object)
		(ball ?b - object)
		(gripper ?g - object)
		(at-robby ?r - object)
		(in ?b ?r - object)
		(free ?g - object)
		(carry ?o ?g - object))

   (:action move
       :parameters  (?from ?to - object)
       :precondition (and  (room ?from) (room ?to) (at-robby ?from))
       :effect (and  (at-robby ?to)
		     (not (at-robby ?from))))



   (:action pick
       :parameters (?obj ?room ?gripper - object)
       :precondition  (and  (ball ?obj) (room ?room) (gripper ?gripper)
			    (in ?obj ?room) (at-robby ?room) (free ?gripper))
       :effect (and (carry ?obj ?gripper)
		    (not (in ?obj ?room)) 
		    (not (free ?gripper))))


   (:action drop
       :parameters  (?obj  ?room ?gripper - object)
       :precondition  (and  (ball ?obj) (room ?room) (gripper ?gripper)
			    (carry ?obj ?gripper) (at-robby ?room))
       :effect (and (in ?obj ?room)
		    (free ?gripper)
		    (not (carry ?obj ?gripper)))))

