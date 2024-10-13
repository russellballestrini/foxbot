#!/usr/bin/python
import requests
import json

def get_stocks_by_tickers( tickers ):
    r = requests.get( "http://finance.google.com/finance/info?client=ig&q=NASDAQ:" + ','.join( tickers ) )
    try:
        return json.loads( r.content.lstrip('\n// ') )
    except ValueError:
        return False

def main( msg ):
    tickers = msg.split()[1:]
    if tickers:
        stocks = get_stocks_by_tickers( tickers )
        if stocks:
            output = []
            for stock in stocks:
                output.append( "%s $%s %s %s%%" % ( stock['t'], stock['l'], stock['c'], stock['cp'] ) )
            return str( ' | '.join( output ) )
    return False


if __name__ == '__main__':
    print main( 'quotes DRI BAC PAY' )

