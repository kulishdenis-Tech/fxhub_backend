# 📱 Flutter Integration Guide

Цей гайд описує як інтегрувати FX Hub Backend API з Flutter мобільним додатком.

## 🌐 API Endpoint

**Base URL:** `https://fxhub-backend.onrender.com`

## ✅ Готовність для Flutter

- ✅ **CORS налаштовано** - дозволено всі origins (тимчасово)
- ✅ **Standardized responses** - уніфікований формат відповідей
- ✅ **Error handling** - структуровані помилки
- ✅ **Health check** - endpoint для перевірки статусу

## 📡 API Endpoints для Flutter

### 1. Health Check

Перевірка доступності API перед основним запитом.

```dart
final response = await http.get(
  Uri.parse('https://fxhub-backend.onrender.com/health'),
);

// Response:
{
  "status": "ok",
  "timestamp": "2025-11-03T12:00:00Z",
  "database": "connected",
  "version": "1.0.0"
}
```

### 2. Найкращі курси (Головний екран)

```dart
final response = await http.get(
  Uri.parse('https://fxhub-backend.onrender.com/rates/bestrate'),
);

// Response:
{
  "success": true,
  "data": [
    {
      "currency": "USD/UAH",
      "buy_best": 41.95,
      "buy_exchanger": "VALUTA_KIEV",
      "buy_timestamp": "2025-11-03T11:21:24",
      "sell_best": 42.00,
      "sell_exchanger": "GARANT",
      "sell_timestamp": "2025-11-03T12:36:00"
    }
  ],
  "meta": {
    "total": 13,
    "limit": null,
    "offset": 0,
    "returned": 13
  }
}
```

**Фільтри:**
```dart
// Фільтр по валютах
Uri.parse('https://fxhub-backend.onrender.com/rates/bestrate?currencies=USD/UAH,EUR/UAH')

// Фільтр по обмінниках
Uri.parse('https://fxhub-backend.onrender.com/rates/bestrate?exchangers=GARANT,MIRVALUTY')

// Пагінація
Uri.parse('https://fxhub-backend.onrender.com/rates/bestrate?limit=10&offset=0')
```

### 3. Список обмінників (Dropdown/Filter)

```dart
final response = await http.get(
  Uri.parse('https://fxhub-backend.onrender.com/exchangers/list'),
);

// Response:
{
  "success": true,
  "data": {
    "exchangers": ["CHANGE_KYIV", "GARANT", "KIT_GROUP", "MIRVALUTY", "SWAPS", "UACOIN", "VALUTA_KIEV"]
  },
  "meta": {
    "count": 7
  }
}
```

### 4. Список валютних пар (Фільтри)

```dart
final response = await http.get(
  Uri.parse('https://fxhub-backend.onrender.com/currencies/list'),
);

// Response:
{
  "success": true,
  "data": {
    "currencies_a": ["CAD", "CHF", "CZK", "EUR", "GBP", "JPY", "PLN", "SEK", "USD"],
    "currencies_b": ["UAH", "USD"],
    "pairs": [
      {"base": "EUR", "quote": "UAH"},
      {"base": "USD", "quote": "UAH"}
    ]
  },
  "meta": {
    "currencies_a_count": 9,
    "currencies_b_count": 2,
    "pairs_count": 13
  }
}
```

### 5. Історія курсів (Графіки)

```dart
final response = await http.get(
  Uri.parse('https://fxhub-backend.onrender.com/rates/history?currency_pair=USD/UAH&days=7&interval=hour'),
);

// Response:
{
  "success": true,
  "data": {
    "currency": "USD/UAH",
    "period_days": 7,
    "interval": "hour",
    "data_points": [
      {
        "timestamp": "2025-11-03T10:00:00Z",
        "buy": 41.95,
        "sell": 42.00,
        "exchanger": "VALUTA_KIEV"
      }
    ]
  },
  "meta": {
    "count": 24,
    "from_date": "2025-10-27T12:00:00Z",
    "to_date": "2025-11-03T12:00:00Z"
  }
}
```

**Параметри:**
- `currency_pair` (required): `USD/UAH`, `EUR/UAH` тощо
- `exchanger` (optional): Фільтр по обміннику
- `days` (optional): 1-30 днів (default: 7)
- `interval`: `hour` або `day` (default: `hour`)

## 🔧 Flutter Models

### Rate Model

```dart
class Rate {
  final String currency;
  final double? buyBest;
  final String? buyExchanger;
  final String? buyTimestamp;
  final double? sellBest;
  final String? sellExchanger;
  final String? sellTimestamp;

  Rate({
    required this.currency,
    this.buyBest,
    this.buyExchanger,
    this.buyTimestamp,
    this.sellBest,
    this.sellExchanger,
    this.sellTimestamp,
  });

  factory Rate.fromJson(Map<String, dynamic> json) {
    return Rate(
      currency: json['currency'],
      buyBest: json['buy_best']?.toDouble(),
      buyExchanger: json['buy_exchanger'],
      buyTimestamp: json['buy_timestamp'],
      sellBest: json['sell_best']?.toDouble(),
      sellExchanger: json['sell_exchanger'],
      sellTimestamp: json['sell_timestamp'],
    );
  }
}
```

### API Response Wrapper

```dart
class ApiResponse<T> {
  final bool success;
  final T data;
  final Map<String, dynamic>? meta;

  ApiResponse({
    required this.success,
    required this.data,
    this.meta,
  });

  factory ApiResponse.fromJson(
    Map<String, dynamic> json,
    T Function(dynamic) fromJsonT,
  ) {
    return ApiResponse(
      success: json['success'] ?? false,
      data: fromJsonT(json['data']),
      meta: json['meta'] as Map<String, dynamic>?,
    );
  }
}
```

## 📝 Приклад використання

```dart
import 'package:http/http.dart' as http;
import 'dart:convert';

class ApiService {
  static const String baseUrl = 'https://fxhub-backend.onrender.com';

  Future<List<Rate>> getBestRates({
    List<String>? currencies,
    List<String>? exchangers,
    int? limit,
    int? offset,
  }) async {
    final uri = Uri.parse('$baseUrl/rates/bestrate').replace(
      queryParameters: {
        if (currencies != null) 'currencies': currencies.join(','),
        if (exchangers != null) 'exchangers': exchangers.join(','),
        if (limit != null) 'limit': limit.toString(),
        if (offset != null) 'offset': offset.toString(),
      },
    );

    final response = await http.get(uri);

    if (response.statusCode == 200) {
      final json = jsonDecode(response.body);
      final apiResponse = ApiResponse<List<Rate>>.fromJson(
        json,
        (data) => (data as List).map((e) => Rate.fromJson(e)).toList(),
      );

      if (apiResponse.success) {
        return apiResponse.data;
      }
    }

    throw Exception('Failed to load rates');
  }

  Future<List<String>> getExchangers() async {
    final response = await http.get(Uri.parse('$baseUrl/exchangers/list'));

    if (response.statusCode == 200) {
      final json = jsonDecode(response.body);
      if (json['success'] == true) {
        return List<String>.from(json['data']['exchangers']);
      }
    }

    throw Exception('Failed to load exchangers');
  }

  Future<Map<String, dynamic>> getCurrencies() async {
    final response = await http.get(Uri.parse('$baseUrl/currencies/list'));

    if (response.statusCode == 200) {
      final json = jsonDecode(response.body);
      if (json['success'] == true) {
        return json['data'];
      }
    }

    throw Exception('Failed to load currencies');
  }
}
```

## ⚠️ Error Handling

Всі endpoints повертають стандартний формат помилок:

```json
{
  "success": false,
  "error": "Internal server error",
  "message": "Detailed error message"
}
```

**HTTP Status Codes:**
- `200` - Success
- `400` - Bad Request (невірні параметри)
- `500` - Internal Server Error

## 🚀 Best Practices

1. **Health Check перший:**
   ```dart
   // Перевіряй /health перед основним запитом
   final health = await checkHealth();
   if (health['status'] == 'ok') {
     // Робити запити
   }
   ```

2. **Кешування:**
   - Список обмінників і валют рідко змінюються - кешуй локально
   - Найкращі курси оновлюються часто - кешуй на 1-2 хвилини

3. **Pagination:**
   - Використовуй `limit=20` для першого екрану
   - Load more при скролі

4. **Error Handling:**
   ```dart
   try {
     final rates = await apiService.getBestRates();
   } catch (e) {
     // Показати повідомлення користувачу
     showErrorSnackBar('Не вдалося завантажити курси');
   }
   ```

5. **Retry Logic:**
   - Render free tier може "засинати" - додай retry з backoff
   - Перший запит може бути повільним (30-60 сек)

## 📊 Приклад екрану

**Головний екран (Best Rates):**
```dart
ListView.builder(
  itemCount: rates.length,
  itemBuilder: (context, index) {
    final rate = rates[index];
    return RateCard(
      currency: rate.currency,
      buyPrice: rate.buyBest,
      buyExchanger: rate.buyExchanger,
      sellPrice: rate.sellBest,
      sellExchanger: rate.sellExchanger,
    );
  },
);
```

**Екран графіка (History):**
```dart
// Використовуй flutter_charts або fl_chart
LineChart(
  data: historyData.dataPoints.map((point) => 
    ChartPoint(
      x: DateTime.parse(point['timestamp']),
      buy: point['buy'],
      sell: point['sell'],
    )
  ).toList(),
)
```

## 🔐 Production CORS

Зараз CORS дозволено для всіх (`*`). Для production обмеж на твій домен:

**TODO в main.py:**
```python
allow_origins=[
    "https://fxhub.app",
    "capacitor://localhost",  # для мобільного додатку
]
```

## 📚 Корисні посилання

- **API Documentation**: https://fxhub-backend.onrender.com/docs
- **ReDoc**: https://fxhub-backend.onrender.com/redoc
- **GitHub**: https://github.com/kulishdenis-Tech/fxhub_backend
