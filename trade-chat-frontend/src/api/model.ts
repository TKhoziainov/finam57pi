import axios from "axios";

export async function sendMessage(
	userQuery: string,
	accountId: string | null
): Promise<{
	text?: string;
	chart?: { x: number; y: number }[];
}> {
	try {
		const response = await axios.post("http://localhost:8011/process_data", {
			user_query: userQuery,
			account_id: accountId,
		});
		return response.data;
	} catch (error) {
		console.error("Ошибка при запросе к серверу:", error);
		return { text: "Ошибка: не удалось получить ответ от сервера" };
	}
}
