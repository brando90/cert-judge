let right_angle_triangle a b c =
  if a <= 0 || b <= 0 || c <= 0 then false (* Ensure valid positive sides *)
  else
    let x, y, z = if a > b && a > c then (b, c, a)
                  else if b > a && b > c then (a, c, b)
                  else (a, b, c) in
    x * x + y * y = z * z;;

(* Test cases *)
let () =
  assert (right_angle_triangle 3 4 5 = true);
  assert (right_angle_triangle 1 2 3 = false);
  assert (right_angle_triangle 10 6 8 = true);
  assert (right_angle_triangle 2 2 2 = false);
  assert (right_angle_triangle 7 24 25 = true);
  assert (right_angle_triangle 10 5 7 = false);
  assert (right_angle_triangle 5 12 13 = true);
  assert (right_angle_triangle 15 8 17 = true);
  assert (right_angle_triangle 48 55 73 = true);
  
  (* Edge cases *)
  assert (right_angle_triangle 1 1 1 = false);
  assert (right_angle_triangle 2 2 10 = false);
  assert (right_angle_triangle 30000 40000 50000 = true);
  assert (right_angle_triangle 5 13 12 = true);
  assert (right_angle_triangle 0 0 0 = false);
  assert (right_angle_triangle (-3) (-4) (-5) = false);
  
  print_endline "Pass!";;
