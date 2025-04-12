/**
 *
 **/
Ext._define('rh.pesquisa.PrevidenciarioRestfulWindow', {
    'extend': 'core.RestfulWindow',

    'rest': 'rh.pesquisa.PrevidenciarioRestful',
    width:500,

    'get_days': function(data1, data2){
      var d1 = new Date(data1.substr(6,4), data1.substr(3,2)-1, data1.substr(0,2));
      var d2 = new Date(data2.substr(6,4), data2.substr(3,2)-1, data2.substr(0,2));
      retorno =  Math.ceil((d2.getTime()-d1.getTime())/1000/60/60/24);
      if (retorno < 0)
        retorno = 0
      retorno = retorno+1
      return retorno;
    },

    'data_inicioField': function(){
      if (!this._data_inicio){
        this._data_inicio = Ext._create('Ext.form.DateField', {
          'fieldLabel': 'Data Início',
          'name': 'data_inicio'
        });
      }
      this._data_inicio.on({
        scope: this,
        change: function(combo, newValue){
          form = this.getFormPanel().getForm()
          var data1 = form.getValues().data_inicio
          var data2 = form.getValues().data_fim

          dias = this.get_days(data1, data2)
          Ext.getCmp('dias').setValue(dias);
        
        }
      });

      return this._data_inicio
    },

    'data_fimField': function(){
      if (!this._data_fim){
        this._data_fim = Ext._create('Ext.form.DateField', {
          'fieldLabel': 'Data Fim',
          'name': 'data_fim',
        });
      }
      this._data_fim.on({
        scope: this,
        change: function(combo, newValue){
          form = this.getFormPanel().getForm()
          var data1 = form.getValues().data_inicio
          var data2 = form.getValues().data_fim
          
          dias = this.get_days(data1, data2)
          Ext.getCmp('dias').setValue(dias);
          
        }
      });
      return this._data_fim
    },

    'getFormPanel': function() {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
              'frame': true,
              'border': false,
              'defaults': {
                'width': 350
              },
              'items': [
             
              {
                fieldLabel: 'Empresa/Orgão',
                xtype: 'textfield',
                allowBlank: true,
                name: 'empresa_orgao'
              },
                this.data_inicioField(),
                this.data_fimField(),
              {
                fieldLabel: 'Dias',
                xtype: 'numberfield',
                allowBlank: true,
                name: 'dias',
                id:'dias',
                disabled:true,
                enableKeyEvents: true
              },
              {
                xtype: 'combo',
                hiddenName: 'tipo_regime',
                fieldLabel: 'Tipo de Regime',
                store: [
                  [1, 'REGIME GERAL DE PREVIDÊNCIA'],
                  [2, 'REGIME PRÓPRIO DE PREVIDÊNCIA'],
                ],
                triggerAction: 'all',
              },
              ]
            });

        return this._formPanel;
    }
});
