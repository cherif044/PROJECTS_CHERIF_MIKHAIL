#!/usr/bin/env python3
"""
RISC-V RV32I Random Test Generator
Generates random instruction sequences with configurable weights, hazards, and loops.
"""

import json
import random
import time
import os
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field


@dataclass
class InstructionObject:
    """Represents a single RISC-V instruction with all necessary fields."""
    mnemonic: str
    format: str
    category: str
    rd: Optional[int] = None
    rs1: Optional[int] = None
    rs2: Optional[int] = None
    imm: Optional[int] = None
    shamt: Optional[int] = None
    label_target_index: Optional[int] = None
    label_name: Optional[str] = None
    raw_word: int = 0
    assembly_text: str = ""
    metadata: Optional[Dict] = None


class RV32IGenerator:
    """Main generator class for RV32I instruction tests."""
    
    def __init__(self, metadata_path: str = "rv32i_metadata.json", 
                 config_path: str = "config_defaults.json"):
        """Initialize generator with metadata and config."""
        self.metadata = self._load_metadata(metadata_path)
        self.config = self._load_config(config_path)
        self.rng = self._make_rng()
        self.seed_used = self.rng.random()  # Store for manifest
        
        # Category to mnemonic mapping
        self.category_map = self._build_category_map()
        
        # Track state for hazard injection
        self.last_rd = None
        self.last_was_load = False
        self.backward_branch_count = 0
        
    def _load_metadata(self, path: str) -> List[Dict]:
        """Load instruction metadata from JSON."""
        with open(path, 'r') as f:
            return json.load(f)
    
    def _load_config(self, path: str) -> Dict:
        """Load configuration from JSON."""
        with open(path, 'r') as f:
            return json.load(f)
    
    def _make_rng(self) -> random.Random:
        """Create PRNG with auto-generated seed from time and PID."""
        seed = (int(time.time_ns()) ^ os.getpid()) & 0xFFFFFFFFFFFFFFFF
        return random.Random(seed)
    
    def _build_category_map(self) -> Dict[str, List[Dict]]:
        """Build mapping from category to list of instruction metadata."""
        cat_map = {}
        for meta in self.metadata:
            cat = meta['category']
            if cat not in cat_map:
                cat_map[cat] = []
            cat_map[cat].append(meta)
        return cat_map
    
    def _weighted_choice(self, weights: Dict[str, float]) -> str:
        """Choose a key from weights dict based on probabilities."""
        items = list(weights.items())
        keys = [k for k, v in items]
        vals = [v for k, v in items]
        return self.rng.choices(keys, weights=vals, k=1)[0]
    
    def _choose_register(self) -> int:
        """Choose a random register (uniform x0..x31)."""
        return self.rng.randint(0, 31)
    
    def _choose_sp_biased_base(self) -> int:
        """Choose base register for memory ops (sp-biased)."""
        if self.rng.random() < self.config['register_policy']['sp_usage_fraction_in_memory_ops']:
            return 2  # x2 = sp
        return self.rng.randint(1, 31)  # Avoid x0 as base
    
    def _choose_imm_arith(self) -> int:
        """Choose arithmetic immediate from buckets."""
        buckets = self.config['immediates']['arith']
        choice = self._weighted_choice({
            'small': buckets['small'],
            'boundary': buckets['boundary'],
            'medium': buckets['medium'],
            'random_full': buckets['random_full'],
            'special_pattern': buckets['special_pattern']
        })
        
        if choice == 'small':
            return self.rng.choice([-1, 0, 1])
        elif choice == 'boundary':
            return self.rng.choice(buckets['boundary_values'])
        elif choice == 'medium':
            return self.rng.randint(-32, 32)
        elif choice == 'special_pattern':
            return self.rng.choice(buckets['special_values'])
        else:  # random_full
            return self.rng.randint(-2048, 2047)
    
    def _choose_shamt(self) -> int:
        """Choose shift amount (uniform 0..31)."""
        return self.rng.randint(0, 31)
    
    def _choose_mem_offset(self) -> int:
        """Choose memory offset with alignment."""
        mem_cfg = self.config['immediates']['memory_offset']
        choice = self._weighted_choice({
            'near_zero': mem_cfg['near_zero'],
            'small_range': mem_cfg['small_range'],
            'mid_range': mem_cfg['mid_range'],
            'far_range': mem_cfg['far_range']
        })
        
        if choice == 'near_zero':
            offset = 0
        elif choice == 'small_range':
            offset = self.rng.randrange(4, mem_cfg['small_range_max'], 4)
        elif choice == 'mid_range':
            offset = self.rng.randrange(64, mem_cfg['mid_range_max'], 4)
        else:  # far_range
            offset = self.rng.randrange(256, mem_cfg['far_range_max'], 4)
        
        # Ensure within 12-bit signed range
        return min(max(offset, -2048), 2047)
    
    def _choose_upper20(self) -> int:
        """Choose 20-bit upper immediate."""
        upper_cfg = self.config['immediates']['upper20']
        if self.rng.random() < upper_cfg['symbolic_fraction']:
            base = self.rng.choice(upper_cfg['symbolic_bases'])
            return (base >> 12) & 0xFFFFF
        else:
            return self.rng.randint(0, 0xFFFFF)
    
    def _choose_branch_target(self, current_idx: int, max_idx: int) -> int:
        """Choose branch target index."""
        br_cfg = self.config['branch_offsets']
        distance_type = self._weighted_choice({
            'near': br_cfg['near'],
            'mid': br_cfg['mid'],
            'far': br_cfg['far']
        })
        
        if distance_type == 'near':
            max_dist = br_cfg['near_max_bytes'] // 4
        elif distance_type == 'mid':
            max_dist = br_cfg['mid_max_bytes'] // 4
        else:
            max_dist = br_cfg['far_max_bytes'] // 4
        
        # Choose direction
        if br_cfg['allow_backward'] and self.rng.random() < 0.5 and current_idx > 0:
            # Backward (potential loop)
            if self.backward_branch_count < self.config['loops']['max_backward_depth']:
                distance = self.rng.randint(1, min(max_dist, current_idx))
                target = current_idx - distance
                self.backward_branch_count += 1
                return max(0, target)
        
        # Forward
        distance = self.rng.randint(1, min(max_dist, max_idx - current_idx - 1))
        return min(current_idx + distance, max_idx - 1)
    
    def _select_mnemonic_in_category(self, category: str) -> Dict:
        """Select a random mnemonic from given category."""
        candidates = self.category_map.get(category, [])
        if not candidates:
            # Fallback to ADDI
            return next(m for m in self.metadata if m['mnemonic'] == 'ADDI')
        return self.rng.choice(candidates)
    
    def _apply_hazard_injection(self, obj: InstructionObject, prev: Optional[InstructionObject]):
        """Apply hazard injection based on probabilities."""
        if not prev:
            return
        
        hazard_cfg = self.config['hazards']
        
        # RAW dependency
        if self.rng.random() < hazard_cfg['raw_dependency_prob']:
            if prev.rd is not None and prev.rd != 0:
                if obj.rs1 is not None:
                    obj.rs1 = prev.rd
                elif obj.rs2 is not None:
                    obj.rs2 = prev.rd
        
        # WAW (write-after-write)
        if self.rng.random() < hazard_cfg['waw_repeat_prob']:
            if prev.rd is not None and obj.rd is not None:
                obj.rd = prev.rd
        
        # Load-use hazard
        if self.last_was_load and self.rng.random() < hazard_cfg['load_use_prob']:
            if self.last_rd is not None and obj.rs1 is not None:
                obj.rs1 = self.last_rd
    
    def _pack_instruction(self, obj: InstructionObject) -> int:
        """Pack instruction object into 32-bit word."""
        meta = obj.metadata
        opcode = int(meta['opcode'], 16)
        funct3 = int(meta['funct3'], 16) if meta['funct3'] else 0
        funct7 = int(meta['funct7'], 16) if meta['funct7'] else 0
        
        fmt = meta['format']
        
        if fmt == 'R':
            word = (funct7 << 25) | (obj.rs2 << 20) | (obj.rs1 << 15) | \
                   (funct3 << 12) | (obj.rd << 7) | opcode
        
        elif fmt == 'I':
            imm = obj.imm if obj.imm is not None else 0
            # Handle shifts specially (funct7 in upper bits)
            if meta['immed_kind'] == 'shamt5':
                shamt = obj.shamt if obj.shamt is not None else 0
                word = (funct7 << 25) | (shamt << 20) | (obj.rs1 << 15) | \
                       (funct3 << 12) | (obj.rd << 7) | opcode
            elif meta['mnemonic'] in ['ECALL', 'EBREAK']:
                # System instructions have specific immediate values
                sys_imm = 0 if meta['mnemonic'] == 'ECALL' else 1
                word = (sys_imm << 20) | (obj.rs1 if obj.rs1 else 0) << 15 | \
                       (funct3 << 12) | (obj.rd if obj.rd else 0) << 7 | opcode
            else:
                imm12 = imm & 0xFFF
                word = (imm12 << 20) | (obj.rs1 << 15) | (funct3 << 12) | \
                       (obj.rd << 7) | opcode
        
        elif fmt == 'S':
            imm = obj.imm if obj.imm is not None else 0
            imm_hi = (imm >> 5) & 0x7F
            imm_lo = imm & 0x1F
            word = (imm_hi << 25) | (obj.rs2 << 20) | (obj.rs1 << 15) | \
                   (funct3 << 12) | (imm_lo << 7) | opcode
        
        elif fmt == 'B':
            # Branch offset encoding
            offset = obj.imm if obj.imm is not None else 0
            bit12 = (offset >> 12) & 1
            bit11 = (offset >> 11) & 1
            bits10_5 = (offset >> 5) & 0x3F
            bits4_1 = (offset >> 1) & 0xF
            word = (bit12 << 31) | (bits10_5 << 25) | (obj.rs2 << 20) | \
                   (obj.rs1 << 15) | (funct3 << 12) | (bits4_1 << 8) | \
                   (bit11 << 7) | opcode
        
        elif fmt == 'U':
            imm20 = (obj.imm if obj.imm is not None else 0) & 0xFFFFF
            word = (imm20 << 12) | (obj.rd << 7) | opcode
        
        elif fmt == 'J':
            # JAL offset encoding
            offset = obj.imm if obj.imm is not None else 0
            bit20 = (offset >> 20) & 1
            bits10_1 = (offset >> 1) & 0x3FF
            bit11 = (offset >> 11) & 1
            bits19_12 = (offset >> 12) & 0xFF
            word = (bit20 << 31) | (bits19_12 << 12) | (bit11 << 20) | \
                   (bits10_1 << 21) | (obj.rd << 7) | opcode
        
        else:
            word = 0x00000013  # NOP fallback
        
        return word & 0xFFFFFFFF
    
    def _render_assembly(self, obj: InstructionObject, label_map: Dict[int, str]) -> str:
        """Render instruction object to assembly text."""
        meta = obj.metadata
        mnem = meta['mnemonic'].lower()
        
        # Special cases
        if mnem in ['ecall', 'ebreak']:
            return mnem
        elif mnem == 'fence':
            return "fence"
        elif mnem == 'fence.i':
            return "fence.i"
        
        # Build operand list
        pattern = meta['operand_pattern']
        operands = []
        
        for op in pattern:
            if op == 'rd':
                operands.append(f"x{obj.rd}")
            elif op == 'rs1':
                operands.append(f"x{obj.rs1}")
            elif op == 'rs2':
                operands.append(f"x{obj.rs2}")
            elif op == 'imm':
                operands.append(str(obj.imm))
            elif op == 'shamt':
                operands.append(str(obj.shamt))
            elif op == 'imm20':
                operands.append(f"0x{obj.imm:x}")
            elif op == 'label':
                operands.append(obj.label_name if obj.label_name else "L_?")
            elif 'imm(rs1)' in op:
                operands.append(f"{obj.imm}(x{obj.rs1})")
            elif op == 'pred_succ':
                operands.append("iorw, iorw")  # Default fence
        
        if operands:
            return f"{mnem} {', '.join(operands)}"
        return mnem
    
    def generate_instruction(self, index: int, length: int, 
                            prev: Optional[InstructionObject]) -> InstructionObject:
        """Generate a single random instruction."""
        # Choose category
        category = self._weighted_choice(self.config['weights'])
        
        # Map weight categories to metadata categories
        cat_mapping = {
            'alu_logic': ['alu', 'compare'],
            'load': ['load'],
            'store': ['store'],
            'branch': ['branch'],
            'jump': ['jump'],
            'upper': ['upper'],
            'system': ['system'],
            'pseudo_nop': ['pseudo'],
            'fence': ['system'],
            'ecall_ebreak': ['system']
        }
        
        valid_cats = cat_mapping.get(category, ['alu'])
        actual_cat = self.rng.choice(valid_cats)
        
        # Select mnemonic
        meta = self._select_mnemonic_in_category(actual_cat)
        
        # Create instruction object
        obj = InstructionObject(
            mnemonic=meta['mnemonic'],
            format=meta['format'],
            category=meta['category'],
            metadata=meta
        )
        
        # Fill operands based on pattern
        pattern = meta['operand_pattern']
        
        for op in pattern:
            if op == 'rd':
                if meta['mnemonic'] == 'JAL' and \
                   self.rng.random() < self.config['register_policy']['ra_usage_fraction_in_jal']:
                    obj.rd = 1  # x1 = ra
                else:
                    obj.rd = self._choose_register()
            elif op == 'rs1':
                obj.rs1 = self._choose_register()
            elif op == 'rs2':
                obj.rs2 = self._choose_register()
            elif op == 'imm':
                obj.imm = self._choose_imm_arith()
            elif op == 'shamt':
                obj.shamt = self._choose_shamt()
            elif op == 'imm20':
                obj.imm = self._choose_upper20()
            elif 'imm(rs1)' in op:
                obj.rs1 = self._choose_sp_biased_base()
                obj.imm = self._choose_mem_offset()
            elif op == 'label':
                # Branch/jump target (will resolve later)
                if index < length - 1:
                    obj.label_target_index = self._choose_branch_target(index, length)
                else:
                    obj.label_target_index = index  # Self-loop if at end
        
        # Apply hazard injection
        self._apply_hazard_injection(obj, prev)
        
        # Track for next iteration
        self.last_rd = obj.rd
        self.last_was_load = (meta['category'] == 'load')
        
        return obj
    
    def generate_test(self, length: int) -> Dict:
        """Generate a complete test of N instructions."""
        print(f"Generating {length} RV32I instructions...")
        
        # Reset state
        self.backward_branch_count = 0
        self.last_rd = None
        self.last_was_load = False
        
        # Generate instructions
        instrs = []
        prev = None
        for i in range(length):
            obj = self.generate_instruction(i, length, prev)
            instrs.append(obj)
            prev = obj
        
        # Resolve labels
        label_map = {}
        for obj in instrs:
            if obj.label_target_index is not None:
                target_idx = obj.label_target_index
                if target_idx not in label_map:
                    label_map[target_idx] = f"L{target_idx}"
                obj.label_name = label_map[target_idx]
        
        # Compute offsets and pack
        for i, obj in enumerate(instrs):
            if obj.label_target_index is not None:
                pc_current = i * 4
                pc_target = obj.label_target_index * 4
                offset = pc_target - pc_current
                
                # Validate offset range
                if obj.format == 'B':
                    # B-type: 13-bit signed, multiple of 2
                    if abs(offset) >= 4096:
                        offset = 4  # Fallback to small forward
                elif obj.format == 'J':
                    # J-type: 21-bit signed, multiple of 2
                    if abs(offset) >= (1 << 20):
                        offset = 4  # Fallback
                
                obj.imm = offset
            
            # Pack instruction
            obj.raw_word = self._pack_instruction(obj)
            obj.assembly_text = self._render_assembly(obj, label_map)
        
        # Generate output
        asm_lines = []
        for i, obj in enumerate(instrs):
            if i in label_map:
                asm_lines.append(f"{label_map[i]}:")
            asm_lines.append(f"    {obj.assembly_text:<30}  # 0x{obj.raw_word:08x}")
        
        hex_lines = [f"{obj.raw_word:08x}" for obj in instrs]
        
        # Create manifest
        manifest = {
            "generator": "RV32I Random Test Generator",
            "version": "1.0",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "seed": self.seed_used,
            "length": length,
            "weights": self.config['weights'],
            "backward_branches": self.backward_branch_count
        }
        
        return {
            "assembly": asm_lines,
            "hex": hex_lines,
            "manifest": manifest,
            "instructions": instrs
        }


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate random RV32I test programs")
    parser.add_argument('-n', '--num-instructions', type=int, default=100,
                       help='Number of instructions to generate (default: 100)')
    parser.add_argument('-o', '--output', type=str, default='test',
                       help='Output file prefix (default: test)')
    
    args = parser.parse_args()
    
    # Create tests directory if it doesn't exist
    tests_dir = "tests"
    os.makedirs(tests_dir, exist_ok=True)
    
    # Create generator
    gen = RV32IGenerator()
    
    # Generate test
    result = gen.generate_test(args.num_instructions)
    
    # Write assembly file
    asm_file = os.path.join(tests_dir, f"{args.output}.S")
    with open(asm_file, 'w') as f:
        f.write("# Auto-generated RISC-V RV32I test\n")
        f.write(f"# Generated: {result['manifest']['timestamp']}\n")
        f.write(f"# Seed: {result['manifest']['seed']}\n")
        f.write(f"# Instructions: {result['manifest']['length']}\n\n")
        f.write(".text\n")
        f.write(".globl _start\n")
        f.write("_start:\n")
        for line in result['assembly']:
            f.write(line + '\n')
        f.write("\n# End of test\n")
    
    print(f"Assembly written to: {asm_file}")
    
    # Write hex file
    hex_file = os.path.join(tests_dir, f"{args.output}.hex")
    with open(hex_file, 'w') as f:
        for line in result['hex']:
            f.write(line + '\n')
    
    print(f"Hex written to: {hex_file}")
    
    # Write binary file
    bin_file = os.path.join(tests_dir, f"{args.output}.bin")
    with open(bin_file, 'w') as f:
        for hex_word in result['hex']:
            word = int(hex_word, 16)
            binary = format(word, '032b')
            f.write(binary + '\n')
    
    print(f"Binary written to: {bin_file}")
    
    # Write manifest
    manifest_file = os.path.join(tests_dir, f"{args.output}_manifest.json")
    with open(manifest_file, 'w') as f:
        json.dump(result['manifest'], f, indent=2)
    
    print(f"Manifest written to: {manifest_file}")
    print(f"\nGeneration complete! Generated {args.num_instructions} instructions.")


if __name__ == '__main__':
    main()
