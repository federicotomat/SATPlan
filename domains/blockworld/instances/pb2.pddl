(define (problem pb2)
   (:domain blocksworld)
   (:objects 
	a - block
	b - block
   )
   (:init (on-table a) (on-table b)  (clear a)  (clear b) (arm-empty))
   (:goal (and (on a b))))