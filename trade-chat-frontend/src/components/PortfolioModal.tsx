import { Button } from "@heroui/button";
import { Input } from "@heroui/input";
import {
	Modal,
	ModalBody,
	ModalContent,
	ModalFooter,
	ModalHeader,
} from "@heroui/modal";
import { useState } from "react";

interface Props {
	isOpen: boolean;
	onSave: (id: string) => void;
}

export function PortfolioModal({ isOpen, onSave }: Props) {
	const [value, setValue] = useState("");

	const handleSave = () => {
		if (value.trim()) {
			onSave(value.trim());
		}
	};

	const onKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
		if (e.key === "Enter") {
			handleSave();
		}
	};

	return (
		<Modal isOpen={isOpen} hideCloseButton>
			<ModalContent>
				<ModalHeader className="flex flex-col gap-1">
					Введите ID портфеля
				</ModalHeader>
				<ModalBody>
					<Input
						placeholder="Ваш ID..."
						value={value}
						onChange={e => setValue(e.target.value)}
						onKeyDown={onKeyDown}
					/>
				</ModalBody>
				<ModalFooter>
					<Button color="primary" onPress={handleSave}>
						Сохранить
					</Button>
				</ModalFooter>
			</ModalContent>
		</Modal>
	);
}
