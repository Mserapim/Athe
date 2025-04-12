Ext._define('planejamento.hiring.supervisor.CloseSupervisorWindow', {
  extend: 'Ext.Window',

  getEndDateField: function() {
      if (!this._endDateField) {
          this._endDateField = Ext._create('Ext.form.DateField', {
              fieldLabel: 'Encerramento',
              name: 'end',
              allowBlank: false,
              value: new Date()
          });
      }

      return this._endDateField;
  },

  getObservationField: function() {
      if (!this._observationField)
          this._observationField = Ext._create('Ext.form.TextArea', {
              fieldLabel: 'Observação',
              name: 'observation',
              allowBlank: 'true',
              height: 250,
              width: 400,
          });

      return this._observationField;
  },

  getFormPanel: function() {
      if (!this._formPanel)
        this._formPanel = Ext._create('Ext.form.FormPanel', {
          frame: true,
          items: [
              this.getEndDateField(),
              this.getObservationField()
          ]
      });

      return this._formPanel;
  },

  getUrlControllerName: function() {
    return core.callAction(this.controllerName, 'close_supervisor');
  },

  commitAction: function() {
      Ext.Ajax.request({
          scope: this,
          url: this.getUrlControllerName(),
          params: {
              pk: this.pk_supervisor,
              end_date: this.getEndDateField().getValue().format('d/m/Y'),
              observation: this.getObservationField().getValue()
          },
          success: function(response, opts) {
              var obj = Ext.decode(response.responseText);

              if (obj.success) {
                  this.supervisorGrid.getStore().reload();
                  Ext.Msg.show({title: 'Encerramento', msg: 'Operação realizada com sucesso', buttons: Ext.Msg.OK});
              } else {
                  Ext.Msg.show({title: 'Atenção!', msg: obj.message, buttons: Ext.Msg.OK});
              }
          },
          failure: function(response, opts) {
              Ext.Msg.show({
                  title: 'Encerrar Fiscal',
                  msg: 'Ocorreu um erro ao encerrar fiscal selecionado',
                  buttons: Ext.Msg.OK
              });
          },
          callback: function() {
              this.destroy();
          }
      });
  },

  toAsk: function() {
      if (!Date.parse(this.getEndDateField().getValue()))
          throw "Informe uma data válida";
      else {
          Ext.Msg.show({
              title: 'Encerrar Fiscal',
              msg: 'Tem certeza que deseja ecerrar Fiscal selecionado?',
              buttons: Ext.Msg.YESNO,
              scope: this,
              fn: function(b) {
                  if (b == 'no')
                      return;
                  else if (b == 'yes')
                      this.commitAction();
              }
          });
      }
  },

  constructor: function(cfg) {
      cfg = (cfg ? cfg : {});

      Ext.apply(cfg, {
          title: 'Encerrar Fiscal',
          autoHeight: true,
          width: 500,
          modal: true,

          items: this.getFormPanel(),

          buttons: [
              {
                  text: 'Encerrar',
                  iconCls: 'icon-agree icon-agree-close-supervisor',
                  scope: this,
                  handler: this.toAsk
              },
              {
                  text: 'Cancelar',
                  // iconCls: '',
                  scope: this,
                  handler: this.destroy
              }
          ]
      });

      planejamento.hiring.supervisor.CloseSupervisorWindow.superclass.constructor.call(this, cfg);
  }
});
