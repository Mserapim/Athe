/*****************************************************************************
*                                                                            *
*                            RELATÓRIO CONTRACHEQUE                          *
*                                                                            *
*****************************************************************************/
Ext._define('rh.gfp.reports.employee.forms.PayCheckMPMT', {
    extend: 'rh.gfp.reports.employee.forms.PayCheck',

    _getParamsList: function() {
        values = this.getForm().getValues()
        
        values['pvf_restrict'] = true;
        return values

    },

    getParams: function (cfg) {
        var params = {
            contracheque: this._paycheckPkList,
            admin: 1,
        };

        return Ext.apply(params, {
            outfile: this.getReportFilename(cfg),
            report_name: this.getReportName(cfg),
        });
    },

    _getStoreOfEndpoint: function (endpoint) {
        if (!this._stores) {
            this._stores = {};
        }

        if (this._stores.hasOwnProperty(endpoint)) {
            return this._stores[endpoint];
        }

        this._stores[endpoint] =  Ext._create('Ext.data.JsonStore', {
            url: core.callAction('GFPReportUsuario', endpoint),
            fields: ['codigo', 'descricao'],
            baseParams: {pvf_restrict: true},
            root: 'result',
            totalProperty: 'totalRows',
            autoLoad: false,
        });

        return this._stores[endpoint];
    },


    _fetchPaycheckList: function (cfg) {
        var mask = new Ext.LoadMask(
            this.ownerCt.getEl() || this.getEl(),
            { msg: 'Processando...' }
        );
        mask.show();

        Ext.Ajax.request({
            url: core.callAction('GFPReportUsuario', 'paycheck_by_period_and_type'),
            params: this._getParamsList(),
            scope: this,
            success: function (xhr) {
                var result = Ext.decode(xhr.responseText);

                if (result.success) {
                    this._paycheckPkList = result.pk;
                    this.requestReport(cfg);
                    return;
                }

                Ext.Msg.show({
                    title: 'Contracheque',
                    msg: result.message,
                    icon: Ext.Msg.ERROR,
                    buttons: Ext.Msg.OK,
                });
            },
            failure: function (xhr) {
                Ext.Msg.show({
                    title: 'Contracheque',
                    msg: 'Recurso indisponível no momento.',
                    icon: Ext.Msg.ERROR,
                    buttons: Ext.Msg.OK,
                });
            },
            callback: function () {
                mask.hide();
            },
        });
    },


});
