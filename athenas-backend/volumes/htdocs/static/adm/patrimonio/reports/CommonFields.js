/**
 * retirement = tipo de baixa
 * acquisition = tipo de aquisição
 * depreciated = depreciado ou reavaliado
 * reportType = analítico ou sintético
 */
Ext._define('adm.patrimonio.reports.CommonFields', {

    _getReportTypeStore: function (extended) {
        if (extended) 
            return [[1, 'ANALÍTICO'], [2, 'SINTÉTICO'], [3, 'RESUMO']];
        else
            return [[1, 'ANALÍTICO'], [0, 'SINTÉTICO']];
    },

    getReportTypeField: function(cfg) {
        if (!this.reportTypeField) {
            var extended = cfg.fields.reportTypeExtended;
            var value = cfg.fields.reportTypeValue;
            this.reportTypeField = Ext._create('Ext.form.ComboBox', {
                hiddenName: 'analitico',
                fieldLabel: 'Relatório',
                store: this._getReportTypeStore(extended),
                allowBlank: false,
                triggerAction: 'all',
                value: value !== undefined ? value : 1
            });
        }
        return this.reportTypeField;
    },

    getAssetsField: function(cfg) {
        if (!this.assetsField) {
            this.assetsField = Ext._create('standard.fields.ChoiceField', {
                fieldLabel: 'Tipo',
                hiddenName: 'proprio',
                choiceId: 'patrimonio.REPORT_TIPO',
                allowBlank: false
            });
        }
        return this.assetsField;
    },

    getInitialDateField: function(cfg) {
        if (!this.initialDateField) {
            this.initialDateField = Ext._create('Ext.form.DateField', {
                name: 'data_inicial',
                fieldLabel: 'De',
                allowBlank: false
            });
        }
        return this.initialDateField;
    },

    getFinalDateField: function(cfg) {
        if (!this.finalDateField) {
            this.finalDateField = Ext._create('Ext.form.DateField', {
                name: 'data_final',
                fieldLabel: 'Até',
                allowBlank: false
            });
        }
        return this.finalDateField;
    },

    getDepartmentField: function(cfg) {
        if (!this.departmentField) {
            this.departmentField = Ext._create('Ext.form.NumberField', {
                name: 'departamento',
                value: cfg.fields.department,
                fieldLabel: 'departamento',
                hidden: true
            });
        }
        return this.departmentField;
    },

    getAcquisitionField: function(cfg) {
        if (!this.acquisitionField) {
            this.acquisitionField = Ext._create('Ext.form.ComboBox', {
                hiddenName: 'tipo_aquisicao',
                fieldLabel: 'Tipo Aquisição',
                store: [
                    ['t', 'TODAS AQUISIÇÕES'],
                    ['i', 'INDIVIDUAL'],
                    ['nota-fiscal', 'NOTA FISCAL'],
                    ['nota-convenio', 'NOTA CONVÊNIO'],
                    ['nota-doacao', 'NOTA DOAÇÃO'],
                    ['nota-entrada', 'NOTA ENTRADA'],
                ],
                allowBlank: false,
                triggerAction: 'all',
            });
        }
        return this.acquisitionField;
    },

    getRetirementField: function(cfg) {
        if (!this.retirementField) {
            this.retirementField = Ext._create('Ext.form.ComboBox', {
                hiddenName: 'tipo_baixa',
                fieldLabel: 'Tipo Baixa',
                store: [
                    ['t', 'TODAS BAIXAS'],
                    ['i', 'INDIVIDUAL'],
                    ['nota-baixa-alienacao', 'NOTA BAIXA ALIENAÇÃO'],
                    ['nota-baixa-sinistro', 'NOTA BAIXA SINISTRO'],
                    ['nota-baixa-inservibilidade', 'NOTA BAIXA INSERVIDADE'],
                    ['nota-baixa-obsolescencia', 'NOTA BAIXA OBSOLESCENCIA'],
                    ['nota-mudanca-classificacao', 'NOTA MUDANÇA CLASSIFICAÇÃO'],
                    ['nota-baixa-deterioracao', 'NOTA BAIXA DETERIORAÇÃO'],
                    ['nota-baixa-doacao', 'NOTA BAIXA DOAÇÃO'],
                    ['nota-baixa', 'NOTA BAIXA'],
                ],
                allowBlank: false,
                triggerAction: 'all',
            });
        }
        return this.retirementField;
    },

    getDepreciatedField: function(cfg) {
        if (!this.depreciatedField) {
            this.depreciatedField = Ext._create('Ext.form.NumberField', {
                name: 'tipo', 
                fieldLabel: 'Tipo',
                hidden: true,
                value: cfg.fields.depreciated
            });
        }
        return this.depreciatedField;
    },

    getAccountField: function(cfg) {
        if (!this.accountField) {
            this.accountField = Ext._create('core.fields.AutocompleteField', {
                fieldLabel: 'Conta',
                name: 'conta',
                rest: 'adm.patrimonio.parametro.ContaRestful',
                gridColumnAction: false
            });
        }
        return this.accountField;
    },

    getGrupoField: function(cfg) {
        if(!this._groupField) {
            this._groupField = Ext._create('core.fields.AutocompleteField', {
                fieldLabel: 'Grupo',
                name: 'grupo',
                rest: 'adm.patrimonio.parametro.GrupoEspecieRestful',
                gridColumnAction: false,
                comboListeners: {
                    scope: this,
                    changevalid: function(combo, value, oldvalue, valid) {
                        if(valid) {
                            this.getEspecieField().setValue('');
                            this.getEspecieField().setPreFilter([{ property: 'grupo', value: value }]);
                        }
                        else {
                            this.getEspecieField().setPreFilter(null);
                        }
                    }
                }
            });
        }
        return this._groupField;
    },

    getEspecieField: function(cfg) {
        if(!this._especieField)
            this._especieField = Ext._create('core.fields.AutocompleteField', {
                fieldLabel: 'Especie',
                name: 'especie',
                rest: 'adm.patrimonio.parametro.EspecieRestful',
                gridColumnAction: false
            });
        return this._especieField;
    },

    getLocationField: function(cfg) {
        if (!this.locationField) {
            this.locationField = Ext._create('core.fields.FoldedRestfulField', {
                restTree: 'adm.patrimonio.localizacao.Tree',
                fieldLabel: 'Localização',
                name: 'localizacao',
                width: 333
            });
        }
        return this.locationField;
    },
});