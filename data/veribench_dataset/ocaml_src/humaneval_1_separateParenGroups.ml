let separate_paren_groups paren_string =
  let rec process chars current_group depth acc =
    match chars with
    | [] -> if depth = 0 && current_group <> "" then List.rev (current_group :: acc) else List.rev acc
    | c :: rest ->
        if c = '(' then
          process rest (current_group ^ "(") (depth + 1) acc
        else if c = ')' then
          let new_group = current_group ^ ")" in
          if depth = 1 then
            process rest "" 0 (new_group :: acc)
          else if depth > 1 then
            process rest new_group (depth - 1) acc
          else
            process rest current_group depth acc (* Handles unexpected unmatched closing parentheses *)
        else (* ignore spaces *)
          process rest current_group depth acc
  in
  process (List.of_seq (String.to_seq paren_string)) "" 0 [];;

(* Test cases *)
let () =
  assert (separate_paren_groups "(()()) ((())) () ((())()())" = ["(()())"; "((()))"; "()"; "((())()())"]);
  assert (separate_paren_groups "() (()) ((())) (((())))" = ["()"; "(())"; "((()))"; "(((())))"]);
  assert (separate_paren_groups "(()(())((())))" = ["(()(())((())))"]);
  assert (separate_paren_groups "( ) (( )) (( )( ))" = ["()"; "(())"; "(()())"]);
  assert (separate_paren_groups "" = []);
  assert (separate_paren_groups "   " = []);
  assert (separate_paren_groups "()" = ["()"]);
  assert (separate_paren_groups "(" = []);
  assert (separate_paren_groups ")" = []);
  assert (separate_paren_groups "()(())" = ["()"; "(())"]);
  assert (separate_paren_groups "  () (())  " = ["()"; "(())"]);
  assert (separate_paren_groups "(  ) ((   )) (( )(   ))" = ["()"; "(())"; "(()())"]);
  print_endline "Pass!";;
