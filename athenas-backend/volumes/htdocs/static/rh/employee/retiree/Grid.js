 Ext._define('rh.employee.retiree.Grid', {
    extend: 'rh.employee.Grid',
    restWindow: 'rh.employee.retiree.Window',

    configOrderToolBar: ['add', 'edit', 'remove', '-', 'report', '-', 'search', '->', '-', 'download'],

    getConfigActionsItems: function(cfg){
        var menu = rh.gfp.payroll.PayrollGrid.superclass.getConfigActionsItems.call(this, cfg);
        menu['report'] = {
            text: 'Gerar Relatório',
            iconCls: 'icon-core icon-core-copy',
            menu: [
                {
                    text: 'Ativo(s)',
                    scope: this,
                    handler: function() { this._buildReport(1) }
                },
                {
                    text: 'Inativo(s)',
                    scope: this,
                    handler: function() { this._buildReport(0) }
                }
            ]
        };
        return menu;
    },

    _buildReport: function(ativo){
        engine.mq.Report.request({
            report: '/to/mpe/rh/servidor/collaborators_report',
            waitMessage: 'Gerando relatório...',
            params: {
                outfile: 'relatorio_aposentado',
                report_name: 'Relatório de Aposentado',
                ativo: ativo,
                tipo: 1
            }
        });
    },

    constructor: function(cfg) {
        rh.employee.retiree.Grid.superclass.constructor.call(this, cfg);
    },

    getColumnModel: function() {
        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    Ext._create('Ext.grid.RowNumberer'),
                    {header: 'Chave', dataIndex: 'pk', width: 55, hidden: true},
                    {
                        header: 'Ativo',
                        dataIndex: 'ativo',
                        width: 70,
                        renderer: toolkit.util.formatIconYesNo,
                    },
                    {header: 'Matrícula', dataIndex: 'matricula', width: 80, renderer: function(value) { return '<div style="text-align:right">' + value + '</div>'; }},
                    {header: 'Nome', dataIndex: 'pessoa_fisica_unicode', id: 'autoExpandColumn'},
                    {header: 'Tipo de Aposentadoria', dataIndex: 'type_retirement_display', width: 220},
                    {header: 'CPF', dataIndex: 'cpf', width: 100},
                    {header: 'Data Nascimento', dataIndex: 'date_born', width: 100, renderer: Ext.util.Format.dateRenderer('d/m/Y')},
                ]
            );
        return this._columnModel;
    },
});

core.RestfulGrid.register(
    'rh.employee.retiree.Restful',
    'rh.employee.retiree.Grid'
);
