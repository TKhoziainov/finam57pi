import { Divider } from "@heroui/react";
import { useEffect, useState } from "react";
import { Chat } from "./components/Chat";
import { PortfolioModal } from "./components/PortfolioModal";
import { usePortfolioId } from "./hooks/usePortfolioId";

export function App() {
	const { portfolioId, savePortfolioId } = usePortfolioId();
	const [modalOpen, setModalOpen] = useState(false);

	useEffect(() => {
		if (!portfolioId) {
			setModalOpen(true);
		}
	}, [portfolioId]);

	const handleSave = (id: string) => {
		savePortfolioId(id);
		setModalOpen(false);
	};

	return (
		<>
			<PortfolioModal isOpen={modalOpen} onSave={handleSave} />
			{!modalOpen && (
				<div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
					<div className="w-[90%] bg-white shadow-lg rounded-2xl overflow-hidden">
						<header className="px-6 py-4">
							<h1 className="text-xl font-semibold">Trade Chat</h1>
						</header>
						<Divider className="my-1" />
						<Chat />
					</div>
				</div>
			)}
		</>
	);
}
