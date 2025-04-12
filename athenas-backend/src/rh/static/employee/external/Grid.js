/**
 *
 **/
Ext._define('rh.employee.external.Grid', {
    extend: 'rh.employee.CollaboratorGrid',
    restWindow: 'rh.employee.external.Window',

    configOrderToolBar: ['add', 'edit', 'remove', '-', 'report', '-', 'search', '->', '-', 'download'],

    getConfigActionsItems: function(cfg){

        var menu = rh.employee.external.Grid.superclass.getConfigActionsItems.call(this, cfg);
        menu['report'] = {
            text: 'Gerar Relatório',
            iconCls: 'icon-core icon-core-copy',
            // menu: [
            //     {
            //         text: 'Ativo(s)',
            //         scope: this,
            //         handler: function() { this._buildReport(1) }
            //     },
            //     {
            //         text: 'Inativo(s)',
            //         scope: this,
            //         handler: function() { this._buildReport(0) }
            //     }
            // ]
        };

        return menu;
    },

    _buildReport: function(ativo){

        engine.mq.Report.request({
            report: '/to/mpe/rh/servidor/collaborators_report',
            waitMessage: 'Gerando relatório...',
            params: {
                outfile: 'relatorio_externos',
                report_name: 'Relatório de Externos sem vínculo',
                ativo: ativo,
                tipo: 2

            }
        });
    }
});


core.RestfulGrid.register(
    'rh.employee.external.Restful',
    'rh.employee.external.Grid'
);
