#  SPDX-License-Identifier: MPL-2.0
#  Copyright 2020-2022 John Mille <john@compose-x.io>

from __future__ import annotations

# Below 2 functions for uniq nested dict sorting out inspired/used from
# https://stackoverflow.com/questions/27374273/how-make-unique-a-list-of-nested-dictionaries-in-python
# Thanks for the help :)


def set_from_dict(input_dict: dict):
    return frozenset(
        (k, set_from_dict(v) if isinstance(v, dict) else v)
        for k, v in input_dict.items()
    )


def uniqfy_list_of_dict(input_list: list[dict]) -> list:
    seen = set()
    result = []
    for dict_in_list in input_list:
        representation = set_from_dict(dict_in_list)
        if representation in seen:
            continue
        result.append(dict_in_list)
        seen.add(representation)
    return result


def handle_lists_merges(
    original_list: list[Union[str, dict, list]],
    override_list: list[Union[str, dict, list]],
    uniqfy=False,
) -> list:
    """
    Function to merge list items.
    Dict/Mappings may be duplicate
    Str may not be duplicate
    Lists trigger recursion, although in compose there is no list of lists in the definition.

    :param list original_list: The original list to add the override ones to
    :param list override_list: The lost of items to add up
    :param bool uniqfy: Whether you are expecting identical dicts which should be filtered to be unique based on key/values.
    """
    final_list: list = []
    # Adding up dict/mappins items
    final_list += [item for item in original_list if isinstance(item, dict)]
    final_list += [item for item in override_list if isinstance(item, dict)]
    if uniqfy:
        final_list = uniqfy_list_of_dict(final_list)

    # Adding up str items
    original_str_items = [item for item in original_list if isinstance(item, str)]
    final_list += list(
        set(
            original_str_items
            + [item for item in override_list if isinstance(item, str)]
        )
    )

    # Adding up lists together.
    origin_list_items = [item for item in original_list if isinstance(item, list)]
    override_list_items = [item for item in override_list if isinstance(item, list)]

    if origin_list_items and override_list_items:
        merged_lists = handle_lists_merges(
            origin_list_items, override_list_items, uniqfy=uniqfy
        )
        final_list += merged_lists
    elif origin_list_items and not override_list_items:
        final_list += origin_list_items
    elif not origin_list_items and override_list_items:
        final_list += override_list_items
    return final_list
