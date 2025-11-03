# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-11-03

### Added
- Initial production release
- FastAPI backend with Supabase integration
- Three main endpoints:
  - `/rates/bestrate` - Best buy/sell rates per currency pair
  - `/exchangers/list` - List of all exchangers
  - `/currencies/list` - List of all currency pairs
- CORS middleware for Flutter mobile app
- `/health` endpoint for monitoring
- Structured logging
- Improved error handling with standardized format
- Render deployment configuration (`render.yaml`)
- Automated testing scripts
- Comprehensive documentation

### Production
- **URL**: https://fxhub-backend.onrender.com
- **Status**: ✅ Operational
- **Database**: Supabase (10,719+ rates records)
- **Exchangers**: 7 active exchangers

## [Unreleased]

### Planned
- `/rates/history` endpoint for charts
- Pagination for `/rates/bestrate`
- Rate limiting
- Caching layer
- Production CORS restrictions (fxhub.app domain)
