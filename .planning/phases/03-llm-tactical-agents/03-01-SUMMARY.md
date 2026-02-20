# Plan 03-01: TDD - LLM Output Parser and Move Validator

## Overview
Successfully implemented the critical safety layer between LLM output and the combat engine using TDD. The parser handles malformed LLM responses and extracts structured data, while the validator ensures moves are legal (correct range, valid targets, within movement limits).

## Deliverables
- `src/agents/llm_parser.py` - LLM output text → LLMResponse Pydantic model
- `src/agents/llm_validator.py` - Move legality validation against CombatState  
- `tests/test_llm_parser.py` - Parser tests covering clean output, malformed output, missing fields
- `tests/test_llm_validator.py` - Validator tests covering legal moves, illegal moves, edge cases

## Key Features
- **Robust parsing**: Handles missing tags, extra preamble, markdown wrapping, case insensitivity
- **Null value normalization**: Converts "none", "stay", "n/a", "-", "" to None
- **Target resolution**: Maps "Fighter (D4)" → "fighter_0" with case-insensitive matching
- **Movement parsing**: Extracts destination from "from E5 to D5" or "D5" formats
- **Action resolution**: Fuzzy matches "Multiattack with Scimitar" to actual creature actions
- **Comprehensive validation**: Checks movement distance, target existence, target alive status, attack range
- **Error feedback**: Provides descriptive error messages for illegal moves

## Test Coverage
- 8+ parser test cases covering edge cases
- 9+ validator test cases covering legal/illegal moves
- All existing tests pass (no regressions)

## Verification
- `python -m pytest tests/test_llm_parser.py -v` ✅
- `python -m pytest tests/test_llm_validator.py -v` ✅  
- `python -m pytest tests/ -v` ✅ (no regressions)

## Issues/Deviations
None. Implementation matches plan requirements exactly.