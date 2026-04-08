let parse_nested_parens paren_string =
  let parse_paren_group s =
    let rec aux depth max_depth = function
      | [] -> max_depth
      | '(' :: xs -> aux (depth + 1) (max (depth + 1) max_depth) xs
      | ')' :: xs -> aux (depth - 1) max_depth xs
      | _ -> failwith "Invalid character in input"
    in
    aux 0 0 (List.of_seq (String.to_seq s))
  in
  let groups = String.split_on_char ' ' paren_string |> List.filter (fun s -> s <> "") in
  List.map parse_paren_group groups;;

(* Test cases *)
let () =
  assert (parse_nested_parens "(()()) ((())) () ((())()())" = [2; 3; 1; 3]);
  assert (parse_nested_parens "() (()) ((())) (((())))" = [1; 2; 3; 4]);
  assert (parse_nested_parens "(()(())((())))" = [4]);

  (* Additional edge case tests *)
  assert (parse_nested_parens "" = []);
  assert (parse_nested_parens "()" = [1]);
  assert (parse_nested_parens "(((())))" = [4]);
  assert (parse_nested_parens "(()) ((()))" = [2; 3]);

  print_endline "Pass!";;
