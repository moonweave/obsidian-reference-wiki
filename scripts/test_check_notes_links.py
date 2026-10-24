import tempfile
import unittest
from pathlib import Path
from check_notes import note_aliases, link_candidates, check


class Links(unittest.TestCase):
    def test_alias_forms(self):
        for field in ['aliases: [DEP, "alias, with comma"]', 'aliases:\n- DEP\n- "alias, with comma"']:
            self.assertEqual(note_aliases('---\n'+field+'\n---\n'), ['DEP', 'alias, with comma'])
        self.assertEqual(note_aliases('---\nalias: DEP\n---\n'), ['DEP'])

    def test_resolution_and_negative_controls(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d).resolve()
            for name in ['concepts/Shared', 'tags/Shared', 'concepts/paper.v2']:
                p=root/(name+'.md'); p.parent.mkdir(exist_ok=True);p.write_text('---\naliases: [DEP]\n---\n')
            names={'Shared':[root/'concepts/Shared.md',root/'tags/Shared.md']}
            aliases={'DEP':[root/'concepts/Shared.md'],'collision':[root/'concepts/Shared.md',root/'tags/Shared.md']}
            source=root/'reader.md'
            resolve=lambda t:link_candidates(t,source,root,names,aliases)
            self.assertEqual(resolve('concepts/Shared'),[root/'concepts/Shared.md'])
            self.assertEqual(resolve('tags/Shared.md'),[root/'tags/Shared.md'])
            self.assertEqual(resolve('DEP'),[root/'concepts/Shared.md'])
            self.assertEqual(len(resolve('Shared')),2)
            self.assertEqual(len(resolve('collision')),2)
            self.assertEqual(resolve('missing/Shared'),[])
            self.assertEqual(resolve('../outside'),[])
            self.assertEqual(resolve('concepts/paper.v2'),[root/'concepts/paper.v2.md'])

    def test_checker_uses_alias_and_exact_path_but_retains_collisions(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d).resolve();(root/'concepts').mkdir();(root/'tags').mkdir()
            (root/'concepts/Shared.md').write_text('---\naliases: [DEP, collision]\n---\n## Body\n')
            (root/'tags/Shared.md').write_text('---\naliases: [collision]\n---\n## Body\n')
            (root/'Reader.md').write_text('[[concepts/Shared]] [[DEP]] [[Shared]] [[collision]] [[Missing]]')
            errors=check(root)['errors']
            self.assertFalse(any('unresolved wikilink' in e and ('DEP' in e or 'concepts/Shared' in e) for e in errors))
            self.assertTrue(any('ambiguous wikilink' in e and '-> Shared ' in e for e in errors))
            self.assertTrue(any('ambiguous wikilink' in e and 'collision' in e for e in errors))
            self.assertTrue(any('unresolved wikilink' in e and 'Missing' in e for e in errors))

    def test_manifest_accepts_existing_library_basename(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d).resolve(); (root/'research').mkdir()
            (root/'research/paper2023.md').write_text('---\ntype: reference-record\nreview_status: partial\n---\n')
            (root/'Source Text Manifest — Pilot.md').write_text('---\ntype: source-text-manifest\nsource_text_basis: native-text\nsource_text_storage: external\nsource_text_page_map: pdf-page-comments\nsource_text_hash: sha256:' + '0'*64 + '\n---\n[[research/paper2023]]')
            errors=check(root, library_scope='research')['errors']
            self.assertFalse(any('manifest must link' in e for e in errors))


if __name__ == '__main__':
    unittest.main()
