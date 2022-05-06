from enum import Enum
from math import ceil, log2
from typing_extensions import Self


def max_order(size: int):
    return ceil(log2(size))


class BlockType(Enum):
    FREE = '-'
    IN_USE = '#'

    def __str__(self):
        return self.value


class Block:

    def __init__(self, first_block_number: int, size: int) -> None:
        if first_block_number < 0:
            raise ValueError
        self.level = max_order(size)
        self.first_block_number = first_block_number

    def __lt__(self, other: Self):
        if not isinstance(other, Block):
            return NotImplemented
        return self.first_block_number < other.first_block_number

    @property
    def last_block_number(self) -> int:
        return self.first_block_number+(2**self.level)-1

    @property
    def size(self) -> int:
        return 2**self.level

    def __repr__(self) -> str:
        return f"({self.first_block_number}-{self.last_block_number})"


class Buddy:
    free_lists: dict[int, list[Block]] = {}
    allocated_lists: dict[int, list[Block]] = {}

    def __init__(self, size: int) -> None:
        block = Block(0, size)
        for i in range(block.level+1):
            self.free_lists[i] = []
            self.allocated_lists[i] = []
        self.free_lists[block.level].append(block)

    def show(self) -> None:
        blocks: list[tuple[Block, BlockType]] = []
        for free_list in self.free_lists.values():
            for block in free_list:
                blocks.append((block, BlockType.FREE))

        for allocated_list in self.allocated_lists.values():
            for block in allocated_list:
                blocks.append((block, BlockType.IN_USE))

        blocks.sort(key=lambda x: x[0])

        def toStr(tuple: tuple[Block, BlockType]) -> str:
            block, type = tuple
            return str(type) * block.size

        print(f'|{"|".join(list(map(lambda l: toStr(l), blocks)))}|')

    def allocate(self, size: int) -> None:
        target_level = max_order(size)

        while not self.free_lists[target_level]:
            working_level = target_level
            try:
                while not self.free_lists[working_level]:
                    working_level += 1
            except:
                print(
                    "That size is no longer allocated. Please free it up or try a smaller size.")
                return
            temp = self.free_lists[working_level].pop(0)
            print(f"(Splitting {temp.first_block_number}/{temp.size})")
            former = Block(temp.first_block_number, 2**(temp.level-1))
            self.free_lists[former.level].append(former)
            latter = Block(former.last_block_number+1, 2**(temp.level-1))
            self.free_lists[latter.level].append(latter)
            self.free_lists[latter.level].sort()

        allocated = self.free_lists[target_level].pop(0)
        self.allocated_lists[allocated.level].append(allocated)
        self.allocated_lists[allocated.level].sort()

        print(
            f"Blocks {allocated.first_block_number}-{allocated.last_block_number} allocated:")

    def free(self, first_block_number: int) -> None:
        target_block: Block
        for allocated_list in self.allocated_lists.values():
            for allocated_block in allocated_list:
                if allocated_block.first_block_number == first_block_number:
                    target_block = allocated_block
                    break
            else:
                continue
            break
        else:
            print('No allocation there.')
            return

        self.allocated_lists[target_block.level].remove(target_block)
        self.free_lists[target_block.level].append(target_block)

        working_level = target_block.level
        while len(self.free_lists[working_level]) >= 2:
            self.free_lists[working_level].sort()
            former = self.free_lists[working_level].pop(0)
            latter = self.free_lists[working_level].pop(0)
            print(
                f'(merging {former.first_block_number}/{former.size} and {latter.first_block_number}/{latter.size})')
            working_level += 1
            self.free_lists[working_level].append(
                Block(former.first_block_number, former.size + latter.size))

        print(
            f"Blocks {target_block.first_block_number}-{target_block.size} freed:")


class Config:
    BLOCK_SIZE = 64


buddy = Buddy(Config.BLOCK_SIZE)
buddy.show()

while True:
    cmd = input(
        'How many blocks do you want to allocate/free?\n').strip().split()

    if not cmd or cmd[0] not in ['q', 'a', 'f']:
        print('commands: ’a’ for allocate, ’f’ for free, and ’q’ for quit.')
        continue

    if cmd[0] == 'q':
        break
    else:
        if cmd[0] == 'a':
            try:
                i = int(cmd[1])
                if i > Config.BLOCK_SIZE or i <= 0:
                    raise ValueError()
            except:
                print('Please enter valid int for the second argument.')
                continue

            buddy.allocate(i)
        elif cmd[0] == 'f':
            try:
                i = int(cmd[1])
                if i > Config.BLOCK_SIZE or i < 0:
                    raise ValueError()
            except:
                print('Please enter valid int for the second argument.')
                continue
            buddy.free(i)

        buddy.show()
        continue
