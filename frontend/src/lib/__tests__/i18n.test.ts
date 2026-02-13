import { describe, it, expect, beforeEach } from 'vitest'
import { t, setLocale, getLocale } from '../i18n'

describe('i18n', () => {
  beforeEach(() => {
    setLocale('en')
  })

  it('returns English text by default for t("app.title")', () => {
    expect(t('app.title')).toBe('DUAT Project Management')
  })

  it('returns Chinese text after setLocale("zh")', () => {
    setLocale('zh')
    expect(t('app.title')).toBe('DUAT 專案管理系統')
  })

  it('returns the key itself as fallback for unknown keys', () => {
    expect(t('unknown.key')).toBe('unknown.key')
  })

  it('interpolates variables correctly', () => {
    expect(t('parse.progress', { current: 5, total: 10 })).toBe(
      'Processing 5 of 10'
    )
  })

  it('interpolates variables correctly in Chinese', () => {
    setLocale('zh')
    expect(t('parse.progress', { current: 5, total: 10 })).toBe(
      '正在處理第 5 筆，共 10 筆'
    )
  })

  it('returns current locale via getLocale()', () => {
    expect(getLocale()).toBe('en')
    setLocale('zh')
    expect(getLocale()).toBe('zh')
  })

  it('switches back to English with setLocale("en")', () => {
    setLocale('zh')
    expect(t('app.title')).toBe('DUAT 專案管理系統')

    setLocale('en')
    expect(t('app.title')).toBe('DUAT Project Management')
    expect(getLocale()).toBe('en')
  })

  it('returns key for malformed keys without a dot separator', () => {
    expect(t('nodot')).toBe('nodot')
  })

  it('returns key when group exists but subkey does not', () => {
    expect(t('app.nonexistent')).toBe('app.nonexistent')
  })
})
