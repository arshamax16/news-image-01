// news-image-01 entry (Node 22, standard library only): the image is the
// entry.png beside this file, drawn in this session by build-image.py, and
// the program copies it to /output/entry.png. Copying a fixed file is
// deterministic: two runs write the same bytes.
//
// Outside the grader's container, MAKEFUN_OUTPUT_DIR stands in for /output:
//   mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts

import { copyFileSync } from 'node:fs';
import { join } from 'node:path';

copyFileSync(new URL('./entry.png', import.meta.url), join(process.env.MAKEFUN_OUTPUT_DIR ?? '/output', 'entry.png'));
