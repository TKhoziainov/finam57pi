import { useState } from "react";

export function usePortfolioId() {
	const [portfolioId, setPortfolioId] = useState<string | null>(() => {
		return localStorage.getItem("portfolioId");
	});

	const savePortfolioId = (id: string) => {
		localStorage.setItem("portfolioId", id);
		setPortfolioId(id);
	};

	return { portfolioId, savePortfolioId };
}
