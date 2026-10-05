import { describe, expect, it } from 'vitest'
import { formatCurrency } from './currency'

describe('formatCurrency', () => {
  it('formats USD with thousands separators', () => {
    expect(formatCurrency(1234)).toBe('$1,234')
  })
})
