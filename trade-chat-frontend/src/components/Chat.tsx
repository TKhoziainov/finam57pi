import { useEffect, useRef, useState } from "react";

import { Divider } from "@heroui/divider";
import { Textarea } from "@heroui/input";
import { Button } from "@heroui/react";
import { SendIcon } from "../helpers/icons";

import ReactECharts from "echarts-for-react";
import { sendMessage } from "../api/model";

type Message = {
	id: string;
	role: "user" | "bot";
	text?: string;
	chartData?: { x: number; y: number }[];
};

export function Chat() {
	const [messages, setMessages] = useState<Message[]>([]);
	const [input, setInput] = useState("");
	const [loading, setLoading] = useState(false);
	const listRef = useRef<HTMLDivElement | null>(null);

	useEffect(() => {
		listRef.current?.scrollTo({
			top: listRef.current.scrollHeight,
			behavior: "smooth",
		});
	}, [messages]);

	const handleSend = async () => {
		const text = input.trim();
		if (!text) return;

		const userMsg: Message = {
			id: String(Date.now()) + "-u",
			role: "user",
			text,
		};
		setMessages(prev => [...prev, userMsg]);
		setInput("");
		setLoading(true);

		try {
			const res = await sendMessage(text, localStorage.getItem("portfolioId"));

			const newMessages: Message[] = [];

			if (res) {
				newMessages.push({
					id: String(Date.now()) + "-b-text",
					role: "bot",
					text: res.text,
				});
			}

			if (res.chart && res.chart.length > 0) {
				newMessages.push({
					id: String(Date.now()) + "-b-chart",
					role: "bot",
					chartData: res.chart,
				});
			}

			setMessages(prev => [...prev, ...newMessages]);
		} catch {
			const errMsg: Message = {
				id: String(Date.now()) + "-e",
				role: "bot",
				text: "Ошибка: не удалось получить ответ",
			};
			setMessages(prev => [...prev, errMsg]);
		} finally {
			setLoading(false);
		}
	};

	const onKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
		if (e.key === "Enter" && e.shiftKey) {
			setInput(input);
		} else if (e.key === "Enter") {
			e.preventDefault();
			handleSend();
		}
	};

	const getChartOptions = (data: { x: number; y: number }[]) => ({
		tooltip: { trigger: "axis" },
		xAxis: {
			type: "category",
			data: data.map(p => p.x),
		},
		yAxis: { type: "value" },
		series: [
			{
				data: data.map(p => p.y),
				type: "line",
				smooth: true,
			},
		],
	});

	return (
		<div className="flex flex-col h-[80vh]">
			<div
				ref={listRef}
				className="flex-1 p-6 overflow-auto space-y-4 bg-gradient-to-b from-white to-gray-50"
			>
				{messages.length === 0 && (
					<div className="text-center text-gray-400">
						Начни разговор — отправь сообщение
					</div>
				)}
				{messages.map(m => (
					<div
						key={m.id}
						className={`flex ${
							m.role === "user" ? "justify-end" : "justify-start"
						}`}
					>
						<div
							className={`${
								m.role === "user"
									? "bg-blue-600 text-white rounded-2xl rounded-br-none"
									: "bg-gray-100 text-gray-900 rounded-2xl rounded-bl-none"
							} p-3 max-w-[70%] min-w-max whitespace-pre-line break-words`}
						>
							{m.chartData ? (
								<ReactECharts
									option={getChartOptions(m.chartData)}
									style={{
										width: "100%",
										minWidth: `${Math.min(
											200 + m.chartData.length * 30,
											600
										)}px`,
										height: `${Math.min(200 + m.chartData.length * 20, 500)}px`,
									}}
								/>
							) : (
								m.text
							)}
						</div>
					</div>
				))}
				{loading && (
					<div className="flex justify-start">
						<div className="bg-gray-100 text-gray-900 rounded-2xl p-3 max-w-[70%]">
							...
						</div>
					</div>
				)}
			</div>
			<Divider className="my-1" />
			<div className="w-full px-[15%] py-3 flex items-center gap-3">
				<Textarea
					className="flex-1"
					placeholder="Напиши сообщение..."
					value={input}
					onChange={e => setInput(e.target.value)}
					onKeyDown={onKeyDown}
					disabled={loading}
					minRows={1}
				/>
				<Button
					isIconOnly
					onPress={handleSend}
					disabled={loading}
					className="mt-auto"
					color="primary"
				>
					<SendIcon />
				</Button>
			</div>
		</div>
	);
}
