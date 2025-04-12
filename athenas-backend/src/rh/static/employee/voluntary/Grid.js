/**
 *
 **/
Ext._define('rh.employee.voluntary.Grid', {
    extend: 'rh.employee.CollaboratorGrid',
    restWindow: 'rh.employee.voluntary.Window',

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
                outfile: 'relatorio_voluntarios',
                report_name: 'Relatório de Voluntários',
                ativo: ativo,
                tipo: 3

            }
        });
    },

    constructor: function(cfg){
    	rh.employee.voluntary.Grid.superclass.constructor.call(this, cfg);
    }

});

core.RestfulGrid.register(
    'rh.employee.voluntary.Restful',
    'rh.employee.voluntary.Grid'
);
