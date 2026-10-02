#!/usr/bin/env node
/* Very simple script wrapper for oxc-minify to minify a single file, since it doesn't provide this. */
import { minifySync } from 'oxc-minify'
import { program } from 'commander';
import { readFileSync, writeFileSync } from 'node:fs';

program.argument('path')
program.parse()
const options = program.opts()

const path = program.args[0]
let data = readFileSync(path, 'utf8')
data = minifySync(path, data, {}).code
writeFileSync(path, data)
