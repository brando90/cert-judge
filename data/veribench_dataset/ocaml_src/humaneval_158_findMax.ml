let find_max words =
  let unique_chars_count word =
    word |> String.to_seq |> List.of_seq |> List.sort_uniq compare |> List.length
  in
  match words with
  | [] -> ""
  | _ -> List.fold_left (fun acc word ->
      let acc_count = unique_chars_count acc in
      let word_count = unique_chars_count word in
      if word_count > acc_count || (word_count = acc_count && word < acc) then word else acc
    ) (List.hd words) words;;

(* Test cases *)
let () =
  assert (find_max ["name"; "of"; "string"] = "string");
  assert (find_max ["name"; "enam"; "game"] = "enam");
  assert (find_max ["aaaaaaa"; "bb"; "cc"] = "aaaaaaa");
  assert (find_max ["abc"; "cba"] = "abc");
  assert (find_max ["play"; "this"; "game"; "of"; "footbott"] = "footbott");
  assert (find_max ["we"; "are"; "gonna"; "rock"] = "gonna");
  assert (find_max ["we"; "are"; "a"; "mad"; "nation"] = "nation");
  assert (find_max ["this"; "is"; "a"; "prrk"] = "this");
  
  (* Edge cases *)
  assert (find_max ["b"] = "b");
  assert (find_max ["play"; "play"; "play"] = "play");
  assert (find_max [] = "");
  assert (find_max ["abcd"; "abdc"; "bacd"] = "abcd");
  assert (find_max ["aaaaaa"] = "aaaaaa");
  
  print_endline "Pass!";;