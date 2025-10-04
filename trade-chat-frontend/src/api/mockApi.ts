export async function sendMessage(): Promise<{
	text: string;
	chart: { x: number; y: number }[];
}> {
	await new Promise(r => setTimeout(r, 600));
	return {
		text: "Стоимость акции в период 2010 - 2025",
		chart: [
			{ x: 2010, y: 50.12 },
			{ x: 2011, y: 55.23 },
			{ x: 2012, y: 53.78 },
			{ x: 2013, y: 60.45 },
			{ x: 2014, y: 62.3 },
			{ x: 2015, y: 65.1 },
			{ x: 2016, y: 63.5 },
			{ x: 2017, y: 68.2 },
			{ x: 2018, y: 70.85 },
			{ x: 2019, y: 72.4 },
			{ x: 2020, y: 75.1 },
			{ x: 2021, y: 78.25 },
			{ x: 2022, y: 80.9 },
			{ x: 2023, y: 83.5 },
			{ x: 2024, y: 85.75 },
			{ x: 2025, y: 88.2 },
		],
	};
}
