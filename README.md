# bdr_update_97_org_items

One-off script to update the MODS of 97 org-items in BDR.

---

## Usage

```
$ python3 ./cli_start.py --pid_filepath "/path/to/foo.txt"
```

---


## XML to add

```
<mods:recordInfo>
  <mods:recordInfoNote type="HallHoagOrgLevelRecord">Organization Record</mods:recordInfoNote>
</mods:recordInfo>
```

---


## Getting the PIDs

### Determining the PIDS

From query:

```
https://repository.library.brown.edu/api/search/?q=rel_is_member_of_collection_ssim:%22bdr:wum3gm43%22%20AND%20%20-mods_record_info_note_hallhoagorglevelrecord_ssim:%22Organization%20Record%22%20AND%20-rel_is_part_of_ssim:*&rows=100&fl=pid&sort=pid%20asc
```

Explanation:

- `rel_is_member_of_collection_ssim:"bdr:wum3gm43"`: Looks for records that are members of the Hall-Hoag collection (bdr:wum3gm43).

- `AND -mods_record_info_note_hallhoagorglevelrecord_ssim:"Organization Record"`: Exclude records where `mods_record_info_note_hallhoagorglevelrecord_ssim` has the value `"Organization Record"` -- because we're looking for the org-items missing this value.

- `AND -rel_is_part_of_ssim:*`: Excludes records that have a value in the `rel_is_part_of_ssim field`, because those would not be org-items.

### Saving the PIDS

Then, with that query, which returns json, I can produce `pids.txt`, using [jq], like this:

_(The query below is all on one line; noting this in case it wraps.)_

```
curl 'https://repository.library.brown.edu/api/search/?q=rel_is_member_of_collection_ssim:%22bdr:wum3gm43%22%20AND%20%20-mods_record_info_note_hallhoagorglevelrecord_ssim:%22Organization%20Record%22%20AND%20-rel_is_part_of_ssim:*&rows=100&fl=pid&sort=pid%20asc' | jq -r '.response.docs[].pid' > ./pids.txt
```

[jq]: <https://github.com/mwilliamson/jq.py>

---

