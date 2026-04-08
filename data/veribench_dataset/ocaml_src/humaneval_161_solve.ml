let explode s =
  let rec exp i acc =
    if i < 0 then acc else exp (i - 1) (s.[i] :: acc)
  in
  exp (String.length s - 1) []

let implode l =
  String.concat "" (List.map (String.make 1) l)

let solve s =
  let has_letters = ref false in
  let result =
    String.map (fun c ->
      if 'a' <= c && c <= 'z' then (has_letters := true; Char.uppercase_ascii c)
      else if 'A' <= c && c <= 'Z' then (has_letters := true; Char.lowercase_ascii c)
      else c
    ) s
  in
  if not !has_letters then implode (List.rev (explode result)) else result

(* Test cases *)
let () =
  assert (solve "AsDf" = "aSdF");
  assert (solve "1234" = "4321");
  assert (solve "ab" = "AB");
  assert (solve "#a@C" = "#A@c");
  assert (solve "#AsdfW^45" = "#aSDFw^45");
  assert (solve "#6@2" = "2@6#");
  assert (solve "#$a^D" = "#$A^d");
  assert (solve "#ccc" = "#CCC");
  assert (solve "" = "");
  assert (solve "!!!" = "!!!");
  assert (solve "AAA" = "aaa");
  assert (solve "a" = "A");
  assert (solve "A" = "a");
  print_endline "Pass!";;