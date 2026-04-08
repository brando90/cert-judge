let even_odd_count num =
  let rec count_digits evens odds = function
    | [] -> (evens, odds)
    | x :: xs ->
        let digit = int_of_char x - int_of_char '0' in
        if digit mod 2 = 0 then count_digits (evens + 1) odds xs
        else count_digits evens (odds + 1) xs
  in
  count_digits 0 0 (List.of_seq (String.to_seq (string_of_int (abs num))));;

(* Test cases *)
let () =
  assert (even_odd_count 7 = (0, 1));
  assert (even_odd_count (-78) = (1, 1));
  assert (even_odd_count 3452 = (2, 2));
  assert (even_odd_count 346211 = (3, 3));
  assert (even_odd_count (-345821) = (3, 3));
  assert (even_odd_count (-2) = (1, 0));
  assert (even_odd_count (-45347) = (2, 3));
  assert (even_odd_count 0 = (1, 0));
  
  (* Additional tests *)
  assert (even_odd_count 24680 = (5, 0));
  assert (even_odd_count 13579 = (0, 5));
  
  print_endline "Pass!";;