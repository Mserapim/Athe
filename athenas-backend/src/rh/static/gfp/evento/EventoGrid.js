/**
 *
 **/
Ext._define('rh.gfp.evento.EventoGrid', {
    extend: 'core.RestfulGrid',

    restWindow: 'rh.gfp.evento.EventoWindow',

    keywordFieldMessage: 'Texto',

    showBoolean: function(value){
        return value ? 'SIM' : 'NÃO'
    },

    getColumnModel: function() {
        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    Ext._create('Ext.grid.RowNumberer'),
                    {header: 'Chave', dataIndex: 'pk', width: 55, hidden: true},
                    {header: 'Número', dataIndex: 'numero', width: 60},
                    {header: 'Título', dataIndex: 'titulo', 'minWidth': 240, id: 'autoExpandColumn'},
                    {header: 'Carater', dataIndex: 'carater_display', width: 150},
                    {header: 'Lançamento', dataIndex: 'lancamento_display', width: 80},
                    {header: 'Tipo', dataIndex: 'tipo', width: 35},
                    // {header: 'Tipo', dataIndex: 'tipo', 'key': 'tipo', width: 90},
                    // {header: 'Cálculo', dataIndex: 'calculo_unicode', width: 240},
                    {header: 'Tipo Cálculo', dataIndex: 'tipo_calculo_display', width: 90},
                    {header: 'Automático', dataIndex: 'automatico', width: 80, renderer: this.showBoolean},
                    {header: 'Consignado', dataIndex: 'aplica_consignado', width: 80, renderer: this.showBoolean},
                    {header: 'Consignável', dataIndex: 'aplica_consignavel', width: 80, renderer: this.showBoolean},
                    // {header: 'Porcentagem', dataIndex: 'pct', width: 100},
                    // {header: 'Patronal', dataIndex: 'pct_patronal', width: 90},
                    
                    // {header: 'Prefixo', dataIndex: 'prefix', width: 60},
                    // {header: 'Sequência', dataIndex: 'sequencia_unicode', width: 145},
                    // {
                    //     header: 'Principal',
                    //     dataIndex: 'principal',
                    //     width: 60,
                    //     renderer: function(value) { return value ? 'SIM' : 'NÃO' }
                    // },
                    // {header: 'Sufixo', dataIndex: 'sufix', width: 60},
                    // {header: 'Título', dataIndex: 'titulo', 'id': 'autoExpandColumn'}
                ]
            );

        return this._columnModel;
    },
});

core.RestfulGrid.register(
    'rh.gfp.evento.EventoRestful',
    'rh.gfp.evento.EventoGrid'
);
