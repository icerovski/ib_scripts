    # COMMISSIONS

    
    commission_statement_array = [
        [
            'Ticker',
            'Base currency',
            'Date',
            'Commission',
            'FX at exit',
            'Commission BGN',
        ]
    ]
    for key, value in tickers_data.items():
        pass

        ticker_total_comission = 0
        exit_commission = exit_line_dict['Commission']
        print(exit_commission)

        commission_data_line = [
            ticker,
            ticker_currency,
            exit_date,
            exit_commission,
            fx_rate_exit,
            fx_rate_exit * exit_commission,
        ]
        commission_statement_array.append(commission_data_line)
        ticker_total_comission += fx_rate_exit * exit_commission

            write_tax_statement_csv(commission_statement_array, 'a')